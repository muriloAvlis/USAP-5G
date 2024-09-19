//
// Created by murilo on 18/09/24.
//

#ifndef DEFER_HPP
#define DEFER_HPP

#include <functional>
#include <iostream>

class Defer {
public:
    explicit Defer(std::function<void()> func) : func_(func) {}

    ~Defer() {
        if (func_) {
            func_();
        }
    }

    Defer(const Defer&) = delete;
    Defer& operator=(const Defer&) = delete;

private:
    std::function<void()> func_;
};

#define defer(code) Defer _defer([&]() { code; })

#endif //DEFER_HPP
