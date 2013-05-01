Exec {
  path => ['/bin/', '/sbin/' , '/usr/bin/', '/usr/sbin/', '/usr/local/bin/']
}

class system-update {
  exec {'apt-get-update':
    command => '/usr/bin/apt-get update'
  }

  package {['python', 'python-pip', 'python-dev', 'php5-cli', 'make']:
    ensure => present,
    require => Exec['apt-get-update'],
  }
}

class virtualenv {
  Class['system-update'] -> Class['virtualenv']

  package {['virtualenv']:
    ensure   => 'installed',
    provider => 'pip',
  }

  exec {'create-virtualenv':
    creates => '/home/vagrant/.virtualenvs/wurfl-python/',
    user => 'vagrant',
    command => 'mkdir -p /home/vagrant/.virtualenvs; virtualenv /home/vagrant/.virtualenvs/wurfl-python',
    require => Package['virtualenv'],
  }

  exec {'install-virtualenv-dependencies':
    user => 'vagrant',
    provider => 'shell',
    command => '. /home/vagrant/.virtualenvs/wurfl-python/bin/activate; pip install ordereddict python-Levenshtein elementtree',
    require => Exec['create-virtualenv'],
  }
}

class user {
  Class['system-update'] -> Class['user']

  file {'/home/vagrant/.profile':
    ensure => present,
    mode => 0644,
    owner => 'vagrant',
    group => 'vagrant',
    source => '/vagrant/extras/vagrant/files/profile',
  }
}

include system-update
include virtualenv
include user
