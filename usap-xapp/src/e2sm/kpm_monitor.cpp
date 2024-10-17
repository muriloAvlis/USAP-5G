//
// Created by Murilo Silva <murilosilva@itec.ufpa.brs>.
//

#include "kpm_monitor.hpp"

std::mutex Kpm_monitor::mtx; // mutex for reveive metrics
uint32_t Kpm_monitor::REPORT_PERIOD;
uint32_t Kpm_monitor::GRANULARITY_PERIOD;

// Shared vars with gRPC server process
std::queue<Kpm_monitor::kpm_ind_fmt_3_t> Kpm_monitor::kpm_ind_fmt_3_queue;
std::condition_variable Kpm_monitor::cv;

Kpm_monitor::ue_ids_t Kpm_monitor::get_ue_ids(ue_id_e2sm_t ue_id_e2sm)
{
    ue_ids_t ue_ids {};

    switch (ue_id_e2sm.type)
    {
    case GNB_UE_ID_E2SM: // For node types: gNB-mono | CU | CU-CP
        // F1AP ID
        if (ue_id_e2sm.gnb.gnb_cu_ue_f1ap_lst != nullptr)
        {
            std::ostringstream oss;
            for (size_t j = 0; j < ue_id_e2sm.gnb.gnb_cu_ue_f1ap_lst_len; j++)
            {
                oss << ue_id_e2sm.gnb.gnb_cu_ue_f1ap_lst[j];
            }
            ue_ids.gnb_cu_ue_f1ap_id = {std::stoull(oss.str())};
        }

        // AMF NGAP ID
        if (ue_id_e2sm.gnb.amf_ue_ngap_id != 0)
        {
            ue_ids.amf_ue_ngap_id = {ue_id_e2sm.gnb.amf_ue_ngap_id};
        }

        // RAN UE NGAP ID
        if (ue_id_e2sm.gnb.ran_ue_id != nullptr)
        {
            ue_ids.ran_ue_id = {*ue_id_e2sm.gnb.ran_ue_id};
        }

        break;
    case GNB_DU_UE_ID_E2SM:
        // F1AP ID
        ue_ids.gnb_cu_ue_f1ap_id = {ue_id_e2sm.gnb_du.gnb_cu_ue_f1ap};

        // RAN UE ID
        if (ue_id_e2sm.gnb_du.ran_ue_id != nullptr)
        {
            ue_ids.ran_ue_id = {*ue_id_e2sm.gnb_du.ran_ue_id};
        }
        break;
    case GNB_CU_UP_UE_ID_E2SM:
        // E1AP ID
        ue_ids.gnb_cu_cp_ue_e1ap_id = {ue_id_e2sm.gnb_cu_up.gnb_cu_cp_ue_e1ap};

        // RAN UE ID
        if (ue_id_e2sm.gnb_cu_up.ran_ue_id != nullptr)
        {
            ue_ids.ran_ue_id = {*ue_id_e2sm.gnb_cu_up.ran_ue_id};
        }
        break;
    default:
        SPDLOG_WARN("Unknown UE ID type {:d}", static_cast<int>(ue_id_e2sm.type));
    }

    return ue_ids;
}

Kpm_monitor::ue_ind_metrics_t Kpm_monitor::get_ue_ind_metrics(kpm_ind_msg_format_1_t const* ind_msg_fmt_1)
{
    assert(ind_msg_fmt_1->meas_info_lst_len > 0);

    ue_ind_metrics_t ue_ind_metrics {};
    metric_t metric {};

    for (size_t j = 0; j < ind_msg_fmt_1->meas_data_lst_len; j++)
    {
        meas_data_lst_t data_item {ind_msg_fmt_1->meas_data_lst[j]};

        for (size_t k = 0; k < data_item.meas_record_len; k++)
        {
            switch (ind_msg_fmt_1->meas_info_lst[k].meas_type.type)
            {
            case meas_type_t::NAME_MEAS_TYPE:
                metric.metric_name = {utils::ba_to_str(&ind_msg_fmt_1->meas_info_lst[k].meas_type.name)};

                if (data_item.meas_record_lst[k].value == INTEGER_MEAS_VALUE)
                {
                    metric.metric_value = {data_item.meas_record_lst[k].int_val};
                } else if (data_item.meas_record_lst[k].value == REAL_MEAS_VALUE)
                {
                    metric.metric_value = {data_item.meas_record_lst[k].real_val};
                } else if (data_item.meas_record_lst[k].value == NO_VALUE_MEAS_VALUE)
                {
                    SPDLOG_WARN("Meas no has value!");
                } else
                {
                    SPDLOG_WARN("Meas value type is not supported!");
                }

                ue_ind_metrics.push_back(metric);

                break;
            case meas_type_t::ID_MEAS_TYPE:
                SPDLOG_WARN("ID_MEAS_TYPE is not supported");
                break;
            default:
                SPDLOG_WARN("Unknown meas type");
            }

            if (data_item.incomplete_flag && *data_item.incomplete_flag == TRUE_ENUM_VALUE)
            {
                SPDLOG_WARN("Measurement Record not reliable");
            }
        }
    }

    return ue_ind_metrics;
}


void Kpm_monitor::kpm_sm_cb(sm_ag_if_rd_t const* rd)
{
    assert(rd != nullptr);
    assert(rd->type == INDICATION_MSG_AGENT_IF_ANS_V0);
    assert(rd->ind.type == KPM_STATS_V3_0);

    // Reading Indication Message Format 3
    kpm_ind_data_t const* ind {&rd->ind.kpm.ind};
    // Header
    kpm_ric_ind_hdr_format_1_t const* hdr_format_1 {&ind->hdr.kpm_ric_ind_hdr_format_1};
    // Payload (message)
    kpm_ind_msg_format_3_t const* msg_format_3 {&ind->msg.frm_3};

    u_int64_t now {utils::get_current_time_in_us()};
    static u_int64_t counter {1};

    {
        std::lock_guard<std::mutex> lock(mtx);
        float latency {static_cast<float>(now - hdr_format_1->collectStartTime) / 1000}; // convert to millisecond
        kpm_ind_fmt_3_t kpm_ind_fmt_3 {}; // stores UE IDs and its metrics

        kpm_ind_fmt_3.latency = latency;
        SPDLOG_DEBUG("Receiving KPM indication message number {:d} with latency {} ms", counter, latency);

        ue_ids_t ue_ids{}; // stores UE IDs
        ue_ind_metrics_t metrics {}; // stores metrics

        // Reported list of measurements per UE
        for (size_t i = 0; i < msg_format_3->ue_meas_report_lst_len; i++)
        {
            // Handle UE ID
            const ue_id_e2sm_t ue_id_e2sm {msg_format_3->meas_report_per_ue[i].ue_meas_report_lst};

            // Fill UE IDs
            ue_ids = {get_ue_ids(ue_id_e2sm)};
            kpm_ind_fmt_3.ue_ids = ue_ids;

            // Fill metrics
            metrics = {get_ue_ind_metrics(&msg_format_3->meas_report_per_ue[i].ind_msg_format_1)};
            kpm_ind_fmt_3.ue_metrics = {metrics};
        }

        if (!kpm_ind_fmt_3_queue.empty())
        {
            kpm_ind_fmt_3_queue.pop(); // queue without buffering
        }

        kpm_ind_fmt_3_queue.push(kpm_ind_fmt_3); // push metrics to queue

        counter++;
    }

    cv.notify_all();
}

test_info_lst_t Kpm_monitor::gen_test_info_lst()
{
    test_info_lst_t test_info_lst {};

    // fill test condition type
    test_info_lst.test_cond_type = {S_NSSAI_TEST_COND_TYPE};
    // It can only be TRUE_TEST_COND_TYPE so it does not matter the type
    // but ugly ugly...
    test_info_lst.S_NSSAI = {TRUE_TEST_COND_TYPE};

    // fill test condition
    test_info_lst.test_cond = static_cast<test_cond_e*>(calloc(1, sizeof(test_cond_e)));
    assert(test_info_lst.test_cond != nullptr);
    *test_info_lst.test_cond = {EQUAL_TEST_COND};

    // fill test value
    test_info_lst.test_cond_value = static_cast<test_cond_value_t*>(calloc(1, sizeof(test_cond_value_t)));
    assert(test_info_lst.test_cond_value != nullptr);
    test_info_lst.test_cond_value->type = OCTET_STRING_TEST_COND_VALUE;
    test_info_lst.test_cond_value->octet_string_value = static_cast<byte_array_t*>(calloc(1, sizeof(byte_array_t)));
    assert(test_info_lst.test_cond_value->octet_string_value != nullptr);
    test_info_lst.test_cond_value->octet_string_value->len = 1;
    test_info_lst.test_cond_value->octet_string_value->buf = static_cast<u_int8_t*>(calloc(test_info_lst.test_cond_value->octet_string_value->len, sizeof(u_int8_t)));
    assert(test_info_lst.test_cond_value->octet_string_value->buf != nullptr);

    test_info_lst.test_cond_value->octet_string_value->buf[0] = {1};

    return test_info_lst;
}

label_info_lst_t Kpm_monitor::gen_kpm_no_label()
{
    label_info_lst_t label_item {};

    label_item.noLabel = static_cast<enum_value_e*>(calloc(1, sizeof(enum_value_e)));
    assert(label_item.noLabel != nullptr);
    *label_item.noLabel = TRUE_ENUM_VALUE;

    return label_item;
}


kpm_act_def_format_1_t Kpm_monitor::gen_act_def_fmt_1(ric_report_style_item_t const* report_style_item)
{
    kpm_act_def_format_1_t act_def_fmt_1 {};

    const size_t sz = report_style_item->meas_info_for_action_lst_len;
    act_def_fmt_1.meas_info_lst_len = sz;

    // Fill meas info list
    act_def_fmt_1.meas_info_lst = static_cast<meas_info_format_1_lst_t*>(calloc(sz, sizeof(meas_info_format_1_lst_t)));
    assert(act_def_fmt_1.meas_info_lst != nullptr);
    for (size_t i=0; i < sz; i++)
    {
        // Meas name
        meas_info_format_1_lst_t *meas_item = &(act_def_fmt_1.meas_info_lst[i]);
        meas_item->meas_type.type = meas_type_t::NAME_MEAS_TYPE;
        meas_item->meas_type.name = copy_byte_array(report_style_item->meas_info_for_action_lst[i].name);

        // Label
        meas_item->label_info_lst_len = 1;
        meas_item->label_info_lst = static_cast<label_info_lst_t*>(calloc(1, sizeof(label_info_lst_t)));
        assert(meas_item->label_info_lst != nullptr);
        meas_item->label_info_lst[0] = gen_kpm_no_label();
    }

    // Granularity Period
    act_def_fmt_1.gran_period_ms = GRANULARITY_PERIOD;

    // 8.3.20 - OPTIONAL
    act_def_fmt_1.cell_global_id = nullptr;

#if defined KPM_V2_03 || defined KPM_V3_00
    act_def_fmt_1.meas_bin_range_info_lst_len = 0;
    act_def_fmt_1.meas_bin_info_lst = nullptr;
#endif

    return  act_def_fmt_1;
}

kpm_act_def_t Kpm_monitor::get_kpm_act_def(ric_report_style_item_t* report_style_item)
{
    assert(report_style_item != nullptr);

    kpm_act_def_t act_def {};

    switch (report_style_item->report_style_type)
    {
    case STYLE_4_RIC_SERVICE_REPORT:
        {
            assert(report_style_item->act_def_format_type == FORMAT_4_ACTION_DEFINITION);

            act_def.type = FORMAT_4_ACTION_DEFINITION;
            // Fill matching condition
            act_def.frm_4.matching_cond_lst_len = 1;
            act_def.frm_4.matching_cond_lst = static_cast<matching_condition_format_4_lst_t *>(calloc(act_def.frm_4.matching_cond_lst_len, sizeof(matching_condition_format_4_lst_t)));
            assert(act_def.frm_4.matching_cond_lst != nullptr);

            // Filter connected UEs by S-NSSAI criteria
            act_def.frm_4.matching_cond_lst[0].test_info_lst = gen_test_info_lst();

            // Fill Action Definition Format 1
            act_def.frm_4.action_def_format_1 = gen_act_def_fmt_1(report_style_item);

            break;
        }
    default:
        SPDLOG_ERROR("Unknown RIC Service Style Type!");
    }

    return act_def;
}


kpm_sub_data_t Kpm_monitor::gen_kpm_sub_data(kpm_ran_function_def_t const* ran_func)
{
    assert(ran_func != nullptr);
    assert(ran_func->ric_event_trigger_style_list != nullptr);

    kpm_sub_data_t sub_data {};

    // Generate Event Trigger
    assert(ran_func->ric_event_trigger_style_list[0].format_type == FORMAT_1_RIC_EVENT_TRIGGER); // only 1 is supported on O-RAN specs
    sub_data.ev_trg_def.type = FORMAT_1_RIC_EVENT_TRIGGER;
    sub_data.ev_trg_def.kpm_ric_event_trigger_format_1.report_period_ms = GRANULARITY_PERIOD;

    // Generate Action Definition
    sub_data.sz_ad = 1;
    sub_data.ad = static_cast<kpm_act_def_t*>(calloc(sub_data.sz_ad, sizeof(kpm_act_def_t)));
    assert(sub_data.ad != nullptr && "Unable to allocate memory for kpm_act_def_t");

    // Multiple Action Definitions in one SUBSCRIPTION message is not supported in this project
    // Multiple REPORT Styles = Multiple Action Definition = Multiple SUBSCRIPTION messages
    ric_report_style_item_t* const report_style_item {&ran_func->ric_report_style_list[0]}; // set Action Definition here
    *sub_data.ad = get_kpm_act_def(report_style_item);

    return sub_data;
}

Kpm_monitor::Kpm_monitor()
{
    SPDLOG_INFO("Initializing KPM Monitor...");
    SPDLOG_INFO("Scanning for E2 nodes on the network");
    nodes = {e2_nodes_xapp_api()};
    while (nodes.len < 1)
    {
        SPDLOG_WARN("No E2 nodes connected to network, retrying...");
        nodes = {e2_nodes_xapp_api()};
    }

    SPDLOG_INFO("{} E2 nodes found", nodes.len);

    // set granularity and report period
    const char* gran_period {std::getenv("GRANULARITY_PERIOD")};
    if (gran_period)
    {
        GRANULARITY_PERIOD = std::stoi(gran_period);
    } else
    {
        GRANULARITY_PERIOD = 1000; // default
    }

    const char* report_period {std::getenv("REPORT_PERIOD")};
    if (report_period)
    {
        REPORT_PERIOD = std::stoi(report_period);
    } else
    {
        REPORT_PERIOD = 1000; // default
    }

    // create handle
    hndl = {static_cast<sm_ans_xapp_t*>(calloc(nodes.len, sizeof(sm_ans_xapp_t)))};
    assert(hndl != nullptr);
}

void Kpm_monitor::Stop()
{
    SPDLOG_WARN("Stopping kpm monitor...");

    for (size_t i = 0; i < nodes.len; i++) {
        // Remove the handle previously returned
        if (hndl[i].success == true)
        {
            // Send subscription delete request to RIC
            rm_report_sm_xapp_api(hndl[i].u.handle);
        }
    }

    // Stop the xApp
    while (try_stop_xapp_api() == false)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    // free memory
    free(hndl);
    free_e2_node_arr_xapp(&nodes);
}

void Kpm_monitor::Start()
{
    // Start Monitor
    for (size_t i = 0; i < nodes.len; i++)
    {
        e2_node_connected_xapp_t* node = &nodes.n[i];

        // get KPM SM index by RAN Function ID
        size_t kpm_idx {utils::find_sm_idx(node, KPM_RF_ID)};

        if (kpm_idx == -1) {
            SPDLOG_WARN("KPM SM ID could not be found in the RAN Function List of E2 node {}, ignoring...", node->id.nb_id.nb_id);
            continue;
        }
        assert(node->rf[kpm_idx].defn.type == KPM_RAN_FUNC_DEF_E && "KPM is not the received RAN Function");

        // if REPORT Service is supported by E2 node, send SUBSCRIPTION
        if (node->rf[kpm_idx].defn.kpm.ric_report_style_list != nullptr)
        {
            // Generate KPM SUBSCRIPTION message
            kpm_sub_data_t sub_data {gen_kpm_sub_data(&node->rf[kpm_idx].defn.kpm)};

            // Send subscription to RIC
            hndl[i] = report_sm_xapp_api(&node->id, KPM_RF_ID, &sub_data, kpm_sm_cb);
            assert(hndl[i].success == true);

            free_kpm_sub_data(&sub_data);
        }
    }

    while (utils::stop_app_flag.load() == false)
    {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    Stop();
}

