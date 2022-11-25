#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Any, Callable, Dict
from .agent_based_api.v1 import exists, register, Result, Service, SNMPTree, State
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.temperature import check_temperature, TempParamType

Section = Dict[str, Any]

_unit_status = {
        0: (State.OK, "DISPLAY OFF"),
        1: (State.OK, "REMOTE OFF"),
        2: (State.OK, "3POS OFF"),
        3: (State.OK, "MONIT OFF"),
        4: (State.OK, "TIMER OFF"),
        5: (State.OK, "ALARM OFF"),
        6: (State.OK, "SHUTDOWN DEL"),
        7: (State.OK, "STAND-BY"),
        8: (State.OK, "TR STBY"),
        9: (State.OK, "ALARM STBY"),
        10: (State.OK, "FANBACK"),
        11: (State.OK, "UNIT ON"),
        12: (State.WARN, "WARNING ON"),
        13: (State.CRIT, "ALARM ON"),
        14: (State.OK, "DAMPER OPEN"),
        15: (State.CRIT, "POWER FAIL"),
        16: (State.OK, "MANUAL"),
        17: (State.OK, "RESTART DELAY"),
}

_oid_description = [
        # oid,      ident,          label,                  parse_func
        ( "384",    "unit_status",  "Unit Status",          lambda v: _unit_status[int(v)] ),
        ( "544",    "temp_ret",     "Return Temperature",   lambda v: float(v) ),
        ( "551",    "temp_sup",     "Supply Temperature",   lambda v: float(v) ),
]



def _get_ident(i: int) -> str:
    return _oid_description[i][1]

def _get_label(i: int) -> str:
    return _oid_description[i][2]

def _get_parse_func(i: Any) -> Callable[[Any], Any]:
    return _oid_description[i][3]

_label2index = { v[2]: i for i, v in enumerate(_oid_description) }

def _get_index_from_label(label: str) -> int:
    return _label2index[label]


def parse_vertiv_carel_boss(string_table: StringTable) -> Section:
    if not string_table:
        return None
    parsed = []
    for i, value in enumerate(string_table[0]):
        ident = _get_ident(i)
        parsef = _get_parse_func(i)
        if parsef:
            value = parsef(value)
        parsed.append(value)
    return parsed

def discover_vertiv_carel_boss(section: Section) -> DiscoveryResult:
    for i, value in enumerate(section):
        yield Service(item=_get_label(i))

def check_vertiv_carel_boss(item: str, params: TempParamType, section: Section) -> CheckResult:
    i = _get_index_from_label(item)
    ident = _get_ident(i)
    value = section[i]
    if ident.startswith("temp_"):
                yield from check_temperature(
                        value,
                        params,
                        unique_name=ident,
                        value_store=value
                )
    else:
        yield Result(state=value[0], summary=value[1])



register.snmp_section(
    name = "vertiv_carel_boss",
    detect = exists(".1.3.6.1.4.1.476.1.42.4.3.32.*"),
    fetch = SNMPTree(
        base = ".1.3.6.1.4.1.476.1.42.4.3.32",
        oids = [ x[0] for x in _oid_description ],
    ),
    parse_function = parse_vertiv_carel_boss,
)

register.check_plugin(
    name = "vertiv_carel_boss",
    service_name = "BOSS %s",
    check_default_parameters = {},
    check_function = check_vertiv_carel_boss,
    discovery_function = discover_vertiv_carel_boss,
    check_ruleset_name="temperature",
)
