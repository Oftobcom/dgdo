#include "matcher.h"

std::string Matcher::assign(const Location&, const std::vector<Driver>& drivers) {
    if (drivers.empty()) return "";
    return drivers[0].id;  // TODO: replace with real logic
}
