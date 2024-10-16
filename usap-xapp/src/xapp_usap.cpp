//
// Created by Murilo Silva on 10/10/24.
//

#include <cstdlib>
#include <thread>
#include <csignal>

#include "spdlog/spdlog.h"
#include "e42_xapp_api.h"

#include "defer.hpp"
#include "e2sm/kpm_monitor.hpp"
#include "server/server.hpp"

int main(int argc, char* argv[])
{
    SPDLOG_INFO("Initializing usap-xapp...");

    // Set xApp signal handler
    std::signal(SIGINT, utils::signal_handler);
    std::signal(SIGTERM, utils::signal_handler);

    // Configure logger
    spdlog::set_level(spdlog::level::debug);

    fr_args_t args {init_fr_args(argc, argv)};

    // REMOVE ME: for dev only
    args.ip = "192.168.100.44";

    // Init xApp
    init_xapp_api(&args);
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Init KPM monitor
    auto kpimon {Kpm_monitor()};
    std::thread kpimon_thread([&kpimon]()
    {
        kpimon.Start();
    });

    // Init gRPC Server
    auto server {E2SM_KPM_ServiceImpl()};
    std::thread server_thread([&server]()
    {
        server.Start();
    });

    // Wait for finishing threads
    kpimon_thread.join();
    server_thread.join();

    return EXIT_SUCCESS;
}
