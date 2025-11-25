#pragma once
#include "domain.h"
#include <vector>
#include <string>

class Matcher {
public:
    // naive assign: first available driver
    std::string assign(const Location& loc, const std::vector<Driver>& drivers);
};