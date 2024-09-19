//
// Created by murilo on 18/09/24.
//

#include "grpc_server.hpp"

// E2 Nodes Info Service
grpc::Status E2NodeServiceImpl::getE2Nodes(grpc::ServerContext* context, const xapp::Empty* request, xapp::e2NodesResponse* response)
{
    e2_node_arr_xapp_t nodes = e2_nodes_xapp_api();
    defer(free_e2_node_arr_xapp(&nodes));

    // return infos by e2node
    for (size_t i = 0; i < nodes.len; ++i)
    {
        // Get E2 node
        e2_node_connected_xapp_t* n = &nodes.n[i];

        // Fill response
        xapp::e2_node_connected_xapp_t* e2node = response->add_e2node();

        // Component Config Add (cca)
        e2node->set_len_cca(n->len_cca);

        // IDs
        e2node->mutable_id()->mutable_nb_id()->set_nb_id(n->id.nb_id.nb_id); // nb_id
        e2node->mutable_id()->set_type(get_ngran_name(n->id.type)); // ran_type
        e2node->mutable_id()->mutable_plmn()->set_mcc(n->id.plmn.mcc); // mcc
        e2node->mutable_id()->mutable_plmn()->set_mnc(n->id.plmn.mnc); // mnc
        e2node->mutable_id()->mutable_plmn()->set_mnc_digit_len(n->id.plmn.mnc_digit_len); // mnc_len

        // just for DU
        if (NODE_IS_DU(n->id.type))
        {
            e2node->mutable_id()->set_cu_du_id(*n->id.cu_du_id);
        }

        // TODO: return supported RF by e2node
    }

    // nodes length
    response->set_len(nodes.len);

    return  grpc::Status::OK;
}

void runServer(const std::string& addr)
{
    E2NodeServiceImpl e2NodeService;

    // Configure server
    grpc::ServerBuilder builder;
    builder.AddListeningPort(addr, grpc::InsecureServerCredentials());

    // Register services on server
    builder.RegisterService(&e2NodeService);

    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());

    std::printf("[xApp-INFO]: gRPC server listening on port %s...\n", addr.c_str());

    server->Wait();
}
