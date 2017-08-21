Feature: 创建集群

  # 统一的认证信息指的是登陆集群主机的所用到用户名,密码等信息是一致的
  # 并且对数据库进行验证时使用统一的用户名和密码
  Scenario: 利用统一的认证信息创建集群
    Given 集群信息
    | username | password |
    | admin    | admin    |
    When create cluster with database monitor user wq and password oracle
    Then can get cluster


  Scenario: 利用统一的认证信息创建集群
    Given a
    When b
    Then c