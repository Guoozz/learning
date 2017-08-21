#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

from behave import *


@given('集群信息')
def step_impl(context):
    context.global_a = 1

@given('login information')
def step_impl(context):
    pass


@when('create cluster with database monitor user {user} and password {password}')
def step_impl(context, user, password):
    pass


@then('can get cluster')
def step_impl(context):
    assert context.a == 1



@given('a')
def step_impl(context):
    pass


@when('b')
def step_impl(context):
    pass

@then('c')
def step_impl(context):
    assert context.global_a == 1