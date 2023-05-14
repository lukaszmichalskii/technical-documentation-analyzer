import time

import nltk.tokenize

from nlp.compile import compile_nlp
from nlp.cross_coref import cross_coref
from nlp.information_extraction import content_filtering, filter_sents, svo
from nlp.pipeline import NLP_PIPELINE_JOBS, PIPELINE
from nlp.pre_processing import remove_special_characters, remove_unicode
from nlp.tfidf import tfidf


class NLPJobRunner:
    def __init__(self, pipeline=None):
        self.pipeline = NLP_PIPELINE_JOBS if pipeline is None else pipeline
        self.lang = compile_nlp('en_core_web_sm', self.pipeline)

        # docs file text
        self.documentation = None

        # pipeline variables
        self.tfidf = list()
        self.human_knowledge = list()
        self.sentences = list()
        self.filtered_content = list()
        self.svo = list()

        # parameters
        self.tfidf_top = 5

    def execute(self, text: str):
        self.documentation = text
        start = time.time()
        if PIPELINE.CLEAN in self.pipeline:
            self.documentation = remove_special_characters(self.documentation)
            self.documentation = remove_unicode(self.documentation)
        print(f"CLEAN: {time.time()-start:.2f}s")
        start = time.time()
        if PIPELINE.CROSS_COREF in self.pipeline:
            self.documentation = cross_coref(self.documentation, self.lang)
        print(f"CROSS_COREF: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.TFIDF in self.pipeline:
            self.tfidf = tfidf(self.documentation)
            self.tfidf_top = self.tfidf_top if self.tfidf_top < len(self.tfidf) else len(self.tfidf)-1
        print(f"TFIDF: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.TOKENIZE in self.pipeline:
            self.sentences = nltk.tokenize.sent_tokenize(self.documentation)
        print(f"TOKENIZE: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.TOPIC_MODELING in self.pipeline:
            pattern = [subject for subject in self.human_knowledge]
            self.filtered_content = content_filtering(self.sentences, pattern)
        print(f"TOPIC_MODELLING: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.CONTENT_FILTERING in self.pipeline:
            top_occur = [content_word[0] for content_word in self.tfidf[:self.tfidf_top]]
            content_filtered = content_filtering(self.sentences, top_occur)
            if len(self.filtered_content) > 0:
                self.filtered_content.extend(content_filtered)
            else:
                self.filtered_content = content_filtered
        print(f"CONTENT_FILTERING: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.BATCH in self.pipeline:
            self.sentences = filter_sents(self.sentences)
            self.sentences.extend([sent for sent in self.filtered_content if sent not in self.sentences])
        print(f"BATCH: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.SVO in self.pipeline:
            for sent in self.sentences:
                triples = svo(sent, self.lang)
                if len(triples) > 0:
                    self.svo.extend(triples)
        print(f"SVO: {time.time() - start:.2f}s")

        return self.svo


if __name__ == '__main__':
    jr = NLPJobRunner()
    # text="""Because every time an landmark is changed, it must be first deleted and then inserted to the tree (as we cannot edit shared elements) the k-d tree should balance itself out."""
    # text="""Test app with implementation of FastSLAM 1.0. Implementation of FastSLAM 1.0 as autonomous system node. Implementation of FastSLAM 2.0 in autonomous system. Integration of path planner with SLAM data. Simultaneous localization and mapping (SLAM) is a part of autonomous system of RT12e. As a name suggests, it is responsible for mapping the track and localizing the car on the mapped track at the same time. It is located in the think part of the see-think-act design pattern. It sits between perception module, motion estimation and path planning module. Based on data provided by perception and motion estimation, SLAM creates a map with localization that is later used by path planning module, that creates a path through a map provided by SLAM. Mapping and localization functionality is encapsulated in ROS2’s SLAM node. This node is running on Autonomous System Master Unit, Ubuntu NVIDIA Jetson AGX PC. ASMU is embedded into RT12e. Based on the SLAM module project for RT12e a BSc thesis was written (in Polish). It is a good introduction into a project, but focuses heavily on mathematics and algorithms behind SLAM. There are numerous algorithms that solve simultaneous localization and mapping problems. They can be divided into:     • Full SLAM: we want to know whole path of the car     • Online SLAM: we are only interested in current location of the car In case of Formula Student autonomous system, we are really only interested in current location of the car. Therefore, only Online SLAM algorithms were considered.  There are two other ways that we can categorize SLAM algorithms. Firstly the type of the map that they create:     • Grid based map: we represent map as a grid, where every cell can be occupied in range of 0-1, where 0 is free space (no object inside the cell) and 1 is fully occupied (there is an object in the cell). Landmark (feature) based map: map is represented as a list of landmarks. Landmark can represent various things like trees, cars, cones etc.. Tracks in Formula Student are represented with cones. Those cones make for brilliant landmarks, based on which map can be built. Therefore, we are interested in algorithms that create landmark based maps. To note, many algorithms are able to build both types of maps, but usually one or other is easier to implement.  Last way to divide SLAM algorithms is by the observation data they work with. Observations can either be:     • Observations with known data associations: every observation can easily be associated with given landmark using some unique property that distinguishes this landmark from others     • Observations with unknown data associations: one can’t associate observation with any landmark. Associations have to be made using current location and observation coordinates. All cones at track are the same (3 colors). This means that we can’t associate observation on observation alone. This means that Formula Student SLAM problem is a SLAM with unknown data associations.  Other properties that we are interested in are:     1. Implementation complexity – the lower the better. Especially because it is first implementation of such a system.     2. Computational complexity – autonomous system is a real-time embedded system. Therefore SLAM algorithm has to work in real-time alongside other AS modules. The faster algorithm, the better. Based on all those assumptions and research performed on available solutions, the following algorithms were considered:     • EKF SLAM     • FastSLAM 1.0     • FastSLAM 2.0  EKF SLAM SLAM algorithm based on Extended Kalman Filter. EKF is a well-known estimator for slightly non-linear processes. It extends Kalman Filter which can only estimate linear processes by local linearization using Jacobians. EKF SLAM is one of the simplest algorithms for SLAM problem. It also gives quite good and accurate results. Its main downside is quite high computational complexity. Because for every update we must update a covariance matrix, which size depends on number of landmarks in the map, the complexity if .  FastSLAM FastSLAM is an algorithm that was develop in order to create a solution that will be suitable for environments, where real-time computation is a must. It estimates location of a robot using particles filter. This allows for estimation of non-linear motion models. Particles filter approach has one more big advantage. Every particle can have its own map. This way we can assume, during the observation update, that robot pose (for this particle) is known. This way every landmark position is independent of other landmarks. Therefore, we can store every landmark in separate 2x2 EKF filter, greatly reducing computational complexity during update. Team decided to implement SLAM module using FastSLAM algorithm. This is mostly dictated by need for an algorithm that will work in real-time parallel to other computationally expensive task running on ASMU’s computer. With great complexity reduction comes only slight accuracy loss. In some situations this accuracy loss might not even be the case. Main disadvantage of FastSLAM 1.0 is neglecting observations in proposal distribution. This means that during update there might be not enough particles that are close to real position. This way we lose accuracy as well as particles will share same history much more often. To fix this problem FastSLAM 2.0 was created. It uses observations to get a better, more accurate proposal distribution. This way it performs better than 1.0. Especially when motion model is noisy. The only draw back is little bit higher complexity and harder implementation. To get best performance from SLAM module, the team decided to implement FastSLAM in version 2.0. Basic implementation of FastSLAM 2.0 results in complexity of  where  is a number of particles and  is a number of landmarks in a map. This can be improved with implementation of better data structures. Firstly in order to reduce overall complexity we have to reduce complexity of data association. With unknown data associations we have to implement a data structure that gives us great performance when accessing elements based on their position on the map. K-D trees are such a structure. They allow to access elements in k-dimensional space (in our case 2D) with average complexity of  where  is a number of elements in a tree. Main problem with k-d trees is that there are hard to balance in changing environment. When we are adding and deleting nodes from tree it can become unbalanced quite quickly. We can combat that with even more complex data structures that are created on top of k-d trees, like for example BKD Trees. In case of SLAM module, it was decided to stick with simple k-d trees as there was no time and real benefit to implement BKD trees (or other similar structures). This is because of second way we will reduce FastSLAM complexity. During resampling procedure with every particle that is copied we need to copy his whole map. This is obviously not optimal as it takes a lot of time. Because realistically most of landmarks of the map are not changed during update (only those in range of sensor) those can be shared between particles, that diverged from one given particle. This can be implemented using smart pointers that will count how many particles (trees) are using given landmark, and when it is not needed anymore, it will be deleted. When some particle wants to change, add or delete landmark, it will create a new path in its k-d tree containing new elements. Because every time an landmark is changed, it must be first deleted and then inserted to the tree (as we cannot edit shared elements) the k-d tree should balance itself out. Therefore implementation of BKD trees was abandoned. For implementation of shared elements, C++’s smart pointers (std::shared_ptr) were used. n desktop PC SLAM in debug build was consuming about 50% CPU (100% overall CPU consumption during that time). While release build was consuming 3-5% of CPU. There was no possibility of running SLAM in debug mode as it couldn’t run in real-time. To fix the issue, profiler test were performed. They showed that under debug, majority of time was spend in Eigen3 procedures. The call stack over Eigen3 functionality was also very big. In ordered to fix the issue, research about Eigen3 performance under debug configuration was performed. This thread showed, that in debug build Eigen3 is using a lot of asserts and other debugging tools. Those massively slow down the calculations. To optimize Eigen3 performance under debug configuration, an -O2 flag was used. This optimalization flag was only used for SLAM node, not for whole system build! This fixed the problem and performance was similar to release configuration. Improvement is also visible in profilers flame graph. In order to properly test k-d trees implementations for SLAM module, series of unit tests were implemented. GTest framework was used as it is supported by ROS2. Unit test were implemented for:     • K-d tree creation     • Insertion     • Deletion     • Nodes sharing between multiple trees     • Nearest neighbor search     • Rectangle range search     • Arc range search Multiple of those test were performed on generated datasets containing 1000, 10000 and 100000 points. Unit test for other functionality than k-d trees wasn’t implemented as SLAM algorithms are highly probabilistic and modeling unit tests for those algorithms doesn’t make sense.  Test Application for FastSLAM 1.0. A test application was created in C++ in order to understand FastSLAM 1.0 algorithm. The app was mocking data from randomly generated map and then SLAM was performed on this data. Visualization was created using matplotlib for C++. Application turned out to be successful. It allowed for better understanding of FastSLAM before implementation in autonomous system.  Simulation testing SLAM pipeline testing was performed in Gazebo simulation. In order to check if SLAM module is working correctly visualization was used. RViz2 visualization shows:     • Cones placement on the map (for best particle)     • Localization of all particles     • SLAM path history – [red colored path]     • Odometry only path history – [purple colored path]     • Real path history which is taken from simulation – [blue colored path]     • Cones covariance     • Observation sensor range     • Observations For purpose of testing following sensors where simulated:     • Camera perception: a special plugin to Gazebo simulation was created, that simulated perception from cameras, allowing for gaussian noise of angle and distance detection as well as simulated delay of perception data arrival.     • IMU sensors with gaussian noise for motion estimation module     • GNSS sensor with gaussian noise for motion estimation module     • Odometry sensors with gaussian noise for motion estimation module."""
    text = """This paper presents a proof of concept of a cones detection algorithm used in the camera vision system
of an autonomous formula of the PWr Racing Team, participating in the Formula Student Driverless
competition. Formula Student Driverless is a worldwide university competition, each year teams compete
in building an autonomous formula. This paper aims to provide a PoC of cones detection module for
the currently developed perception system. The positions of the cones seen through the camera are then
used by the car’s autonomous system to drive.
Figure 1: The PWr Racing Team formula during the acceleration discipline at pre-season tests Krzywa,
Poland 2023. In Formula Student Driverless competitions, there are static and dynamic disciplines. The static
disciplines are focused on rating the car’s design, the documentation of each of the car’s systems, and
the management of the team. In dynamic disciplines, the physical and autonomous capabilities of the
car are tested. In all dynamic disciplines, the car is placed on a track, marked by four types of traffic
cones, as depicted in Figure 2.
Figure 2: The traffic cone variants are used to delineate the track in dynamic disciplines. The big orange
with two stripes is used to make the start and end of the race track. Blue and yellow cones are used to
mark the left and right sides of the road, respectively.
There are four different dynamic disciplines; there is Acceleration, Skid-pad, Trackdrive, and Autocross.
In the acceleration dynamic event, the car has to drive through a straight track as fast as possible.
The acceleration discipline is designed to test the car’s speed capabilities as well as its ability to steer
in a stable way to keep a straight direction. In the skid-pad dynamic event, the car has to drive in an eight-shaped circuit, as depicted in Figure 3. The car first drives two laps on the right side of the
track and then transitions and drives two laps on the left side after which it exits the track. The skidpad
discipline tests the ability of the autonomous system to correctly track the stage the car is in and execute
the following transitions. The trackdrive and autocross dynamic disciplines are similar to each other.
They both consist of driving in a closed–loop unknown track of length up to 1 km. The difference is that
in the autocross discipline, the car has to drive only a single lap, while in the trackdrive the car drives
10 laps. By measuring only a single lap time in the autocross, the focus is put on the car’s ability to
drive through a track it has never seen before, while in the trackdrive discipline the focus is on the car’s
ability to adapt to the track and optimize its driving throughout the 10 lap drive. In Figure 1 you can
see the PWr Racing Team formula after finishing the acceleration test. The autonomous system of the car is responsible for everything from observing the environment using
sensors, planning a trajectory through the track from the observations and sending the right commands
to the car’s actuators to correctly follow a trajectory.
Figure 4: High level See-Think-Act data flow diagram. Modules of SEE part are responsible for data
acquisition and observations. THINK’s part modules do all decision- making that are later executed by
modules in ACT part. Camera recognition is a component of the control pipeline of the SEE part of an autonomous system. It
is responsible for detecting objects in real-time and creating a field of cones for further use in the path
planner. Camera recognition is a ROS2 node running on the autonomous system main unit (NVIDIA
Jetson AGX Xavier). The main goal of this project is to develop a cones detection module based
on Formula Student environments. This paper will not describe the hardware implementation on the
system’s main unit, algorithms used for coordinates estimation, and camera fusion (merging detections
from both cameras and LiDAR). In the autonomous system information flow diagram fig. 4 developed
sub-system is Computer Vision node. The task of object detection consists of detecting objects in an image by predicting bounding boxes around
them and correctly determining the class of each detected object. It is a common and popular problem,
that has been studied in the fields of computer vision and artificial intelligence for several decades. The
YOLO (You Only Look Once) object detection deep learning model was introduced in 2015 by Joseph
Redmon and achieved significantly faster detection speeds than any available solution at that time
that was mainly based on classification using convolutional neural networks and a dynamic windowing
approach (R CNN, Fast R CNN, Faster R CNN). With 45 frames per second (FPS) for the large version
and 155 FPS for the smaller version YOLO algorithm was a groundbreaking solution. Despite this speed
increase, YOLO also achieved competitive mAP (mean Average Precision) results with state-of-the-art
detectors. YOLO approaches object detection as a single regression other than a classification problem,
training a convolutional neural network end-to-end to receive an image as input and output the positions
of bounding boxes and their associated classes. Since the publication of the original YOLO paper, there
have been several improved iterations, such as YOLO9000 [1] and YOLOv3 [2], as well as other single
CNN end-to-end models like SSD (Single-Shot MultiBox Detector) [3], Retina-net [4], and SqueezeDet
[5], all of which have matched or surpassed the performance of two-stage detectors in terms of mAP
and detection speed. These models are commonly referred to as 'single-stage object detectors'. Since
mentioned algorithms are defined as supervised machine learning solutions, the crucial process is to
prepare a dataset for the learning routine. You Only Look Once algorithm as mentioned in Object Detection section is a state-of-the-art object
detection algorithm and is almost a standard way of detecting objects in computer vision, that
outperformed all the previous object detection algorithms based on the dynamic windowing approach.
Because of its potential the latest research led to the development of YOLOv8, released on 10th January
2023. Researchers created performance tests on COCO datasets and the results can be seen in fig. 5. Object localization is solved using bounding boxes. Instead of classifying an image as 0, 1 where 0 tells
us that desired object has not been detected on the image and 1 that there is detection. The algorithm
outputs the information about bounding box localization as presented in equation 1, where C1, C2, C3
are classes of the object in this project there are cones (we do not differentiate big orange and orange
cones), PC is the probability of object is there, Bx, By , Bh is bounding box properties. This approach
will work for a single object in the image. n case there are multiple objects the YOLO algorithm divides the image into a grid map of size N xN .
Then using training data and localization of the object (bounding box centroid) it will check if the cell
contains such a point and for each cell create an output vector containing pieces of information mentioned
in equation 1. This means the computed data is a three-dimensional array N xM xV , where N xN is grid
map size and V is vector length. Using this approach the CNN will learn from the training dataset
containing images and estimate output. Prediction is achieved by only one forward propagation pass
and that is why it is called You Only Look Once.
The potential issue is detection of multiple bounding boxes, this case is managed by merging estimated
areas using IOU (intersection over union) eq. 2. Using the IOU metric, the algorithm estimates overlapped boxes and pick the one with the highest
probability value. The described process is known as Non-Max Suppression. What if the cell contains two centroids of different class objects? The cell represented by a vector in
equation 1 is able to encode only one class of object by setting appropriate Ci value. Instead of having
this e.g. 7 dimension vector algorithm concatenate two vectors each for specific detection. This concept
is called anchor boxes. By resizing the grid frequency we can overcome these problems. During RT13e tests on the Krzywa track (3rd March 2023 & 25.03.2023) a lot of recordings were collected.
The detailed report from tests can be seen in table 1. Due to temperature (-8o) both cameras have
problems with power and were discharging very fast, 15 minutes was not sufficient to charge the battery
and change after each test drive during 03.03.2023 tests. In the end, around 20GB of recordings containing
cones is sufficient for project purposes.
 CVAT open source application enables split recording in MP4 format to frames. Images then are easy
to label with cones bounding boxes using predefined classes in LabelImg or CVAT tool. Example of
annotated image fig. 7. The annotation procedure follows rules introduced in section Data Preparation.
Recordings resolution is not very high, due to this there are some limitations when it comes to annotation
and labeling the data for the algorithm. Bad weather forces us to skip cones that are hard to recognize on
the image because of distance or colors impossible to designate by humans while looking at the picture.
An example of cones that were neglected during annotation can be seen in fig. 6. We also have to
handle scenarios where the sun is pointed to the camera lens and generates noise, for this purpose we use
recordings from 25.03.2023 tests on Krzywa where the weather conditions were better and label video
frames respectively, see fig. 6 or 9.
Figure 6: Annotated image from Autocross event during tests, Krzywa 25.03.2023. YOLO CNN (Convolutional Neural Network) has been trained based on a training and cross-validation
set consisting of 200 and 30 annotated images respectively. The training was performed for 1000 epochs
with an additional stop criterion set to 50 epochs (stop training early if no improvement was observed in
the last 50 epochs). As starting point, we used the pre-trained medium-size YOLOv8 Ultralytics model
and make use of the transfer learning approach. The initial setup used a CPU-compatible PyTorch
version and did not take advantage of GPU power causing a huge waste of time resources and performance.
After closer investigation, the environment was configured with CUDA 11.7 support and deep learning
was made using NVIDIA GeForce RTX 3060 GPU which saves a lot of time and significantly improves
the performance of training. Working 1.0 version gave positive feedback for further improvements in
the model and allowed us to detect system bottlenecks. A closer look at the results of training gives us
more insights into improvements in the model e.g. better dataset split (200:29 too small cross-validations
set). The main problem was underfitting and a lot of false positive detections leading to poor SLAM
(Simultaneous Localization and Mapping) and Path-Planner performance (with a confidence threshold
of 0.5 a lot of false positives, see fig.10). This is a crucial problem and could be overcome by using
more data. Another important topic is detection range and complexity of the feed-forward algorithm on
large neural networks that could bring a real impact on autonomous systems when it comes to real-world
scenarios (all ROS2 nodes running simultaneously on NVIDIA Jetson main unit), consider switching to
a small Ultralytics model and compare performance. Version 2.0 used the pre-trained 1.0 model for the deep learning procedure. To overcome the
underfitting/false positives problem we use the FSOCO dataset which was released recently on a free
license without further contribution needed. The dataset contains almost 12k images labeled by Formula
Student teams from around the world. During development of the 2.0 version dataset was split in
a 70:30 ratio where 70% of images went to train data and the rest 30% to the cross-validation set.
For deep learning tasks, a previously configured environment was used (CUDA, GPU-based learning).
Training last around 16 hours and was stopped after 276 epochs, the stop criterion detect that there
is no significant improvement. By increasing the number of unseen environments, the model overcomes
problems from the previous version and works very well on a confidence threshold set to 0.75 in a 10
meters field of view. Validation of the model was performed on multiple recordings from tests with
different weather conditions: high fog and noise from the sun (sun point to the camera lens). Version
2.0 of the camera perception module, provides reliable output up to 10 meters with more than 75%
confidence, it is sufficient for the cones detection part. More data about the environment is gathered
using a LiDAR sensor and by merging these observations we are able to develop a well-performing SEE
component for our autonomous system."""
    sents = jr.execute(text)

    for s in sents:
        print(s)
