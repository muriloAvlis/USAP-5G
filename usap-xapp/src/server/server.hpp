//
// Created by murilo on 14/10/24.
//

#ifndef SERVER_HPP
#define SERVER_HPP

#include <grpcpp/grpcpp.h>
#include "protobuf/xapp.grpc.pb.h"
#include "spdlog/spdlog.h"

#include "e2sm/kpm_monitor.hpp"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using xapp::E2SM_KPM_Service;
using xapp::KPMIndicationRequest;
using xapp::KPMIndicationResponse;
using xapp::UEInfos;
using xapp::UEIDs;
using xapp::MeasInfo;

class E2SM_KPM_ServiceImpl : public E2SM_KPM_Service::Service
{
public:
    E2SM_KPM_ServiceImpl();
    Status GetIndicationStream(grpc::ServerContext* context, const xapp::KPMIndicationRequest* request, grpc::ServerWriter<xapp::KPMIndicationResponse>* writer) override;

    // Start gRPC server
    void Start();

    static void Stop();

private:
    static std::unique_ptr<Server> server;
    ServerBuilder builder;
    std::string server_address {};
    std::mutex mtx;
};



#endif //SERVER_HPP
