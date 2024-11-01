//
// Created by murilo on 14/10/24.
//

#include "server.hpp"

std::unique_ptr<Server> E2SM_KPM_ServiceImpl::server {};

E2SM_KPM_ServiceImpl::E2SM_KPM_ServiceImpl()
{
    // Check server IP and Port
    const char* server_ip {std::getenv("SERVER_IP")};
    const char* server_port {std::getenv("SERVER_PORT")};

    if ((server_ip != nullptr && std::strlen(server_ip) > 0) && (server_port != nullptr && std::strlen(server_port) > 0))
    {
        server_address = std::string(server_ip) + ':' + std::string(server_port);
        // SPDLOG_INFO("gRPC server address set to {}", server_address);
    } else
    {
        SPDLOG_ERROR("Server IP and port cannot be empty!");
        std::raise(SIGINT); // exit xapp
    }
}


Status E2SM_KPM_ServiceImpl::GetIndicationStream(grpc::ServerContext* context,
                                                     const xapp::KPMIndicationRequest* request,
                                                     grpc::ServerWriter<xapp::KPMIndicationResponse>* writer)
{
    SPDLOG_INFO("Receive a request from {} service to GetIndicationStream method, handling...", request->svc_name());

    while (true)
    {
        std::unique_lock<std::mutex> lock(mtx);

        Kpm_monitor::cv.wait(lock, [] { return !Kpm_monitor::kpm_ind_fmt_3_queue.empty(); }); // wait for KPM monitor

        auto metrics = Kpm_monitor::kpm_ind_fmt_3_queue.front(); // get metrics

        // Prepare response
        KPMIndicationResponse response;

        // Latency
        response.set_collectstarttime(metrics.collect_start_time);

        // UE Infos
        UEInfos *ue_infos = {response.mutable_ue()};

        // UE IDs
        UEIDs *ue_ids = {ue_infos->mutable_ue_id()};

        ue_ids->set_gnb_cu_ue_f1ap_id(metrics.ue_ids.gnb_cu_ue_f1ap_id);
        ue_ids->set_amf_ue_ngap_id(metrics.ue_ids.amf_ue_ngap_id);
        ue_ids->set_gnb_cu_cp_ue_e1ap_id(metrics.ue_ids.gnb_cu_cp_ue_e1ap_id);
        ue_ids->set_ran_ue_id(metrics.ue_ids.ran_ue_id);

        // UE metrics
        for (size_t i = 0; i < metrics.ue_metrics.size(); i++)
        {
            MeasInfo *meas_info = {ue_infos->add_ue_meas_info()}; // add new metric

            meas_info->set_meas_name(metrics.ue_metrics.at(i).metric_name);

            // check if the value is integer or real
            if (std::holds_alternative<u_int64_t>(metrics.ue_metrics.at(i).metric_value))
            {
                u_int64_t int_val {std::get<u_int64_t>(metrics.ue_metrics.at(i).metric_value)};
                meas_info->set_int_value(int_val);
            } else if (std::holds_alternative<double>(metrics.ue_metrics.at(i).metric_value))
            {
                double real_val {std::get<double>(metrics.ue_metrics.at(i).metric_value)};
                meas_info->set_real_value(real_val);
            }
        }

        // Send response
        if (!writer->Write(response))
        {
            SPDLOG_WARN("GetIndicationStream interrupted, exiting...");
            break;
        }

        // free queue for new metrics
        Kpm_monitor::kpm_ind_fmt_3_queue.pop();
    }

    return Status::OK;
}

void E2SM_KPM_ServiceImpl::Stop()
{
    if (server)
    {
        SPDLOG_WARN("Stopping server");
        server->Shutdown();
        server->Wait();
    }
}

void E2SM_KPM_ServiceImpl::Start()
{
    // Register services
    E2SM_KPM_ServiceImpl kpm_service;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&kpm_service);

    // Start server
    server = {builder.BuildAndStart()};
    SPDLOG_INFO("Server listening on {}", server_address);

    while (!utils::stop_app_flag.load())
    {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}

