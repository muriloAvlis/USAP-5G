//
// Created by murilo on 18/09/24.
//

#ifndef GRPC_SERVER_HPP
#define GRPC_SERVER_HPP

// gRPC libs
#include <grpc/grpc.h>
#include <grpc/impl/codegen/port_platform.h>
#include <grpc/support/log.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include "pb/xapp.pb.h"
#include "pb/xapp.grpc.pb.h"

// FlexRIC Libs
#include <flexric/src/xApp/e42_xapp_api.h>

// Local libs
#include "defer.hpp"

// E2Nodes service
class E2NodeServiceImpl final : public xapp::e2NodesInfo::Service {
public:
    // rpc getE2Nodes
    grpc::Status getE2Nodes(grpc::ServerContext* context, const xapp::Empty* request, xapp::e2NodesResponse* response) override;
};

// Call to run gRPC server
void runServer(const std::string& addr);

#endif //GRPC_SERVER_HPP
