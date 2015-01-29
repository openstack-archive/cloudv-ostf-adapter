# Cloud Validation adapter for OSTF

## Overview

Existing [OSTF](http://docs.mirantis.com/fuel-dev/develop/ostf_contributors_guide.html)
code provides a number of tests which cover a number of cases needed for cloud
validation. The downside of existing OSTF is that it is tightly coupled with
FUEL's nailgun. Given project aims to create standalone adapter for OSTF which
is independent of FUEL thus making it possible to run OSTF tests on any random
cloud (in theory).

## High-level design

 1. Adapter runs as a standalone service;
 2. Adapter uses OSTF package as dependency;
 3. Adapter has REST APIs to run and terminate tests.

## Links

 * [OSTF contributor's guide](http://docs.mirantis.com/fuel-dev/develop/ostf_contributors_guide.html)
 * [OSTF source code](https://github.com/stackforge/fuel-ostf)

