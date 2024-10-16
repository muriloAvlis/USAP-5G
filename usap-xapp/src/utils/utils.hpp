//
// Created by murilo on 11/10/24.
//

#ifndef UTILS_HPP
#define UTILS_HPP

#include <atomic>
#include <string>
#include <map>
#include "spdlog/spdlog.h"

#include "e2_node_connected_xapp.h"

namespace utils
{
    // xApp control
    inline std::atomic<bool> stop_app_flag(false);

    size_t find_sm_idx(e2_node_connected_xapp_t *node, int rf_id);

    // handle EXIT signals
    void signal_handler(int signum);

    u_int64_t get_current_time_in_us();

    std::string ba_to_str(byte_array_t const* ba);

    void config_logger();
}

#endif //UTILS_HPP
