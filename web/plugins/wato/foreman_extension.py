#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# check_foreman by Marc Sauer
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  Ovirt Plugin is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    Tuple,
)

from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _generate_general_check_options():
        return Dictionary(
                elements=[
                        ("SATELLITE_API_USER", TextAscii(title=_("Satellite / Foreman API User"),
                                         allow_empty=False,
                                         help = _("The user which will connect to the API."),
                                         )
                        ),
                        ("SATELLITE_API_TOKEN", Password(title=_("Satellite / Foreman API token"),
                                        allow_empty=False,
                                        help = _("You can generate an API token in the web interface."),
                                        )
                        ),
                        ("insecure", FixedValue(
                          True,
                          title=_("Disable TLS certificate validation"),
                          totext=_("TLS certificate validation is disabled"),
                        )),
                        ("simulation", FixedValue(
                          True,
                          title=_("Enable simulation mode"),
                          totext=_("Enable simulation mode"),
                        )),
                ]
        )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name = "check_foreman",
        group = RulespecGroupCheckParametersApplications,
        match_type = "dict",
        item_spec = _generate_general_check_options,
        title = lambda: _("Check Foreman settings"),
    )
)