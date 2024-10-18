//
// Created by murilo on 11/10/24.
//

#include "utils.hpp"


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
    SPDLOG_ERROR("Received a stop signal {}, finishing xApp processes", signum);
    stop_app_flag.store(true);

    // Stop KPM Monitor
    Kpm_monitor::Stop();

    // Stop gRPC Server
    E2SM_KPM_ServiceImpl::Stop();

    exit(0);
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

void utils::config_logger()
{
    // define default console log
    auto console = spdlog::stdout_color_st("usap-xapp");

    const char* log_level = std::getenv("LOG_LEVEL");

    std::map<std::string, spdlog::level::level_enum> log_levels = {
        {"DEBUG", spdlog::level::debug},
        {"INFO", spdlog::level::info},
        {"WARN", spdlog::level::warn},
        {"ERROR", spdlog::level::err},
        {"TRACE", spdlog::level::trace},
        {"CRITICAL", spdlog::level::critical},
        {"OFF", spdlog::level::off}
    };

    if (log_level)
    {
        std::string log_level_str = log_level;

        // transform to upper case
        std::transform(log_level_str.begin(), log_level_str.end(), log_level_str.begin(), ::toupper);

        auto it = log_levels.find(log_level_str);
        if (it != log_levels.end()) // match log level
        {
            console->set_level(it->second);
        } else
        {
            console->set_level(spdlog::level::debug); // default
        }
    } else
    {
        console->set_level(spdlog::level::debug); // default
    }

    spdlog::set_default_logger(console);
}
