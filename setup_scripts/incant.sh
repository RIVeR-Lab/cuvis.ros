#!/bin/bash
docker run --ipc=host --network host -it --rm \
-v /home/$USER/projects:/projects -v /home/$USER/colcon_ws/src:/colcon_ws/src --workdir="/colcon_ws/src" \
-i cubert
