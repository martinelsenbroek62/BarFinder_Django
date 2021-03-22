## Before deploy/update server

* Change in vars/deploy.yml vars for deploy/update
* Change in ./inventory host and vars for him

## Use ansible for deploy/update servers :

* ``ansible-playbook universal.yml --extra-vars="target=develop"`` (target = host in inventory and vars for him )
