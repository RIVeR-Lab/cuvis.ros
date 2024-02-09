https://github.com/cubert-hyperspectral/cuvis.ros.git

# Prereqs

You need docker working on your system, with a docker group.

```sudo apt-get install docker.io``` 

```sudo groupadd docker```

```sudo usermod -aG docker $USER```

```newgrp docker```

If you don't configure the docker group correctly, you will need sydo for the following commands
# Installation

Clone this repo onto your computer's ros workspace, and change the branch to foxy.
```mkdir -p ~/colcon_ws/src && cd ~/colcon_ws/src && git clone git@github.com:RIVeR-Lab/cuvis.ros.git && cd cuvis.ros && git checkout foxy```

```./setup_scripts/install.sh```

```./setup_scripts/build.sh```

```ip link set $ETH_INTERNET_NAME mtu 9000```
```double check:```
```ip addr | grep mtu```


# Running

```./setup_scripts/setup_camera_connection.sh # may not work with more than one ethernet connection``` 

```./setup_scripts/incant.sh```

# Within the docker container, run 

```. /ros2_source_install/install/local_setup.bash && source /opt/ros/foxy/setup.bash && cd /colcon_ws && colcon build && source /colcon_ws/install/setup.bash```

```. /install/venv_3.9/bin/activate && export CUVIS="Linux"# need to use the venv for cubert``` 
