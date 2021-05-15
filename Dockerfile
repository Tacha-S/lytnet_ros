FROM tacha/cuda-melodic

ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/bin:${PATH}

RUN apt-get update && \
    apt-get install -y --no-install-recommends libffi-dev liblzma-dev libreadline-dev python3-pip && \
    git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc && \
    eval "$(pyenv init -)" && \
    pip3 install --no-cache-dir pipenv &&\
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-catkin-pkg-modules python3-numpy python3-yaml ros-melodic-cv-bridge && \
    pip3 install --no-cache-dir rospkg empy &&\
    rm -rf /var/lib/apt/lists/*

RUN mkdir ros &&\
    cd ros &&\
    catkin init &&\
    catkin config -DPYTHON_EXECUTABLE=/usr/bin/python3 -DPYTHON_INCLUDE_DIR=/usr/include/python3.6m -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.6m.so &&\
    git clone https://github.com/ros-perception/vision_opencv.git src/vision_opencv &&\
    cd src/vision_opencv/ &&\
    git checkout melodic && \
    /bin/bash -c "source /opt/ros/melodic/setup.bash;catkin build" && \
    echo "source /ros/devel/setup.bash" >> /root/.bashrc

COPY . /ros/src/lytnet_ros

RUN cd /ros/src/lytnet_ros && \
    pipenv install --python 3.6

RUN cd /ros && \
    /bin/bash -c "source /opt/ros/melodic/setup.bash;catkin build"
