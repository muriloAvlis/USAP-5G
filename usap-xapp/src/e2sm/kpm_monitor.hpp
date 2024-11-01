//
// Created by Murilo Silva <murilosilva@itec.ufpa.br>
//

#ifndef KPM_MONITOR_HPP
#define KPM_MONITOR_HPP

#include <queue>
#include <csignal>
#include "e42_xapp_api.h"
#include "spdlog/spdlog.h"
#include "defer.hpp"
#include "utils/utils.hpp"


class Kpm_monitor {
public:
    // types
    using ue_ids_t = struct
    {
        u_int64_t gnb_cu_ue_f1ap_id = 1;
        u_int64_t amf_ue_ngap_id = 2;
        // Guami_t Guami = 3; // Not implemented :)
        u_int32_t gnb_cu_cp_ue_e1ap_id = 4;
        u_int64_t ran_ue_id = 5;
    };

    using metric_t = struct
    {
        std::string metric_name;
        std::variant<u_int64_t, double> metric_value;
    };

    using ue_ind_metrics_t = std::vector<metric_t>;

    using kpm_ind_fmt_3_t = struct
    {
        u_int64_t collect_start_time;
        ue_ids_t ue_ids;
        ue_ind_metrics_t ue_metrics;
    };

    // Shared vars with gRPC server process
    static std::queue<kpm_ind_fmt_3_t> kpm_ind_fmt_3_queue;
    static std::condition_variable cv;

    // prepare args for subscription
    explicit Kpm_monitor();

    // Run monitor
    void Start();

    // Stop Monitor
    static void Stop();

private:
    // Constants
    static std::mutex mtx; // Mutex to control received metrics
    static sm_ans_xapp_t *hndl; // KPM subscription handle
    static e2_node_arr_xapp_t nodes; // Connected E2 nodes
    const int KPM_RF_ID = 2;
    static uint32_t GRANULARITY_PERIOD; // in milliseconds
    static uint32_t REPORT_PERIOD; // in milliseconds

    // Gen KPM subscription data
    static kpm_sub_data_t gen_kpm_sub_data(kpm_ran_function_def_t const* ran_func);

    static kpm_act_def_t get_kpm_act_def(ric_report_style_item_t *report_style_item);
    static test_info_lst_t gen_snssai_test_info_lst(u_int8_t sst);
    static test_info_lst_t gen_ul_rsrp_test_info_lst(int64_t testValue);

    // Action Definitions
    static kpm_act_def_format_1_t gen_act_def_fmt_1(ric_report_style_item_t const* report_style_item);

    // Gen Labels
    static label_info_lst_t gen_kpm_no_label();

    // Callback
    static void kpm_sm_cb(sm_ag_if_rd_t const* rd);

    // fill UE ID
    static ue_ids_t get_ue_ids(ue_id_e2sm_t ue_id_e2sm);

    // fill metrics
    static ue_ind_metrics_t get_ue_ind_metrics(kpm_ind_msg_format_1_t const* ind_msg_fmt_1);
};



#endif //KPM_MONITOR_HPP
