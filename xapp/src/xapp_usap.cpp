//
// Created by Murilo C. da Silva on 17/09/24.
//

#include "xapp_usap.hpp"


int main(int argc, char *argv[])
{
    fr_args_t args = init_fr_args(argc, argv);

    // TEMP
    args.ip = {"192.168.100.44"};

    // Init xApp
    init_xapp_api(&args);
    sleep(1);

    // Start gRPC server
    std::string server_addr = {"0.0.0.0:5051"};
    runServer(server_addr); // lock execution here

    while (try_stop_xapp_api() == false)
    {
        usleep(1000);
    }

    return 0;
}
