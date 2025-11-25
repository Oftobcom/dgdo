#pragma once
#include "domain.h"
#include <vector>
#include <string>

class Matcher {
public:
    std::string assign(const Location& loc,
                       const std::vector<Driver>& drivers);
};
