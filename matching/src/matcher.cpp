#include "matcher.h"

std::string Matcher::assign(const Location&, const std::vector<Driver>& drivers) {
    if (drivers.empty()) return std::string("");
    return drivers[0].id;
}