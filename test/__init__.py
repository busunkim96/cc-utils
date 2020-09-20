# SPDX-FileCopyrightText: 2019 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import sys
import os

# add modules from root dir to module search path
# so unit test modules can use regular imports
sys.path.extend(
    (
        os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            os.pardir
        ),
        os.path.realpath(os.path.dirname(__file__)),
        os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            os.pardir,
            'cli',
        ),
        os.path.realpath(os.path.dirname(__file__)),
    )
)
