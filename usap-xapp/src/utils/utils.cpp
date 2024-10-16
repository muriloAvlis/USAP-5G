//
// Created by murilo on 11/10/24.
//

#include "utils.hpp"

#include "spdlog/spdlog.h"


size_t utils::find_sm_idx(e2_node_connected_xapp_t *node, int rf_id)
{
    for (size_t i = 0; i < node->len_rf; i++)
    {
        if (node->rf[i].id == rf_id)
        {
            return i;
        }
    }
    return -1;
}

void utils::signal_handler(int signum)
{
    SPDLOG_ERROR("Received a stop signal {}, finishing xApp processes...", signum);
    stop_app_flag.store(true);
}

u_int64_t utils::get_current_time_in_us() {
    // get current time
    auto now = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch());

    return duration.count();
}

// convert a type byte_array_t to string
std::string utils::ba_to_str(byte_array_t const* ba)
{
    return std::string{reinterpret_cast<const char*>(ba->buf), ba->len};
}
