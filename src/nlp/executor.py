import time

import networkx as nx
import nltk.tokenize
import pandas as pd
from matplotlib import pyplot as plt
from nltk import CoreNLPParser

from nlp.compile import compile_nlp
from nlp.cross_coref import cross_coref
from nlp.information_extraction import content_filtering, filter_sents, svo, spo
from nlp.pipeline import NLP_PIPELINE_JOBS, PIPELINE
from nlp.pre_processing import remove_special_characters, remove_unicode
from nlp.tfidf import tfidf


class NLPJobRunner:
    def __init__(self, pipeline=None):
        self.pipeline = NLP_PIPELINE_JOBS if pipeline is None else pipeline
        self.lang, self.ner = compile_nlp('en_core_web_sm', self.pipeline)
        self.pos_tagger = CoreNLPParser(url='http://0.0.0.0:9000', tagtype='pos')

        # docs file text
        self.documentation = None

        # pipeline variables
        self.tfidf = list()
        self.human_knowledge = list()
        self.sentences = list()
        self.filtered_content = list()
        self.svo = list()
        self.spo = list()

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
                svo_triples = svo(sent, self.lang)
                if len(svo_triples) > 0:
                    self.svo.extend(svo_triples)
        print(f"SVO: {time.time() - start:.2f}s")
        start = time.time()
        if PIPELINE.SPO in self.pipeline:
            for sent in self.sentences:
                spo_triple = spo(sent, self.pos_tagger)
                if spo_triple and spo_triple not in self.spo:
                    self.spo.append(spo_triple)
        print(f"SPO: {time.time() - start:.2f}s")
        return self.spo, self.svo


if __name__ == '__main__':
    jr = NLPJobRunner()
    text = """Simultaneous localization and mapping (SLAM) is a part of autonomous system of RT12e.
As a name suggests, it is responsible for mapping the track and localizing the car on the mapped track at the same time.
It is located in the think part of the see-think-act design pattern.
It sits between perception module, motion estimation and path planning module.
Based on data provided by perception and motion estimation, SLAM creates a map with localization that is later used by path planning module, that creates a path through a map provided by SLAM.
Mapping and localization functionality is encapsulated in ROS2’s SLAM node.
This node is running on Autonomous System Master Unit, Ubuntu NVIDIA Jetson AGX PC.
ASMU is embedded into RT12e.
Based on the SLAM module project for RT12e a BSc thesis was written (in Polish).
It is a good introduction into a project, but focuses heavily on mathematics and algorithms behind SLAM.
There are numerous algorithms that solve simultaneous localization and mapping problems.
They can be divided into 2 approaches.
Full SLAM we want to know whole path of the car.
Online SLAM: we are only interested in current location of the car.
In case of Formula Student autonomous system, we are really only interested in current location of the car.
Therefore, only Online SLAM algorithms were considered.
There are two other ways that we can categorize SLAM algorithms.
Firstly the type of the map that they create.
Grid based map: we represent map as a grid, where every cell can be occupied in range of 0-1, where 0 is free space (no object inside the cell) and 1 is fully occupied (there is an object in the cell).
Landmark (feature) based map: map is represented as a list of landmarks.
Landmark can represent various things like trees, cars, cones etc..
Tracks in Formula Student are represented with cones.
Those cones make for brilliant landmarks, based on which map can be built.
Therefore, we are interested in algorithms that create landmark based maps.
To note, many algorithms are able to build both types of maps, but usually one or other is easier to implement.
Last way to divide SLAM algorithms is by the observation data they work with.
Observations can either be observations with known data associations: every observation can easily be associated with given landmark using some unique property that distinguishes this landmark from others or observations with unknown data associations: one can’t associate observation with any landmark.
Associations have to be made using current location and observation coordinates.
All cones at track are the same (3 colors). This means that we can’t associate observation on observation alone. This means that Formula Student SLAM problem is a SLAM with unknown data associations.
Other properties that we are interested in are:
1. Implementation complexity – the lower the better.
Especially because it is first implementation of such a system.
2. Computational complexity – autonomous system is a real-time embedded system.
Therefore SLAM algorithm has to work in real-time alongside other AS modules.
The faster algorithm, the better.
Based on all those assumptions and research performed on available solutions, the following algorithms were considered: EKF SLAM, FastSLAM 1.0, FastSLAM 2.0.
SLAM algorithm based on Extended Kalman Filter.
EKF is a well-known estimator for slightly non-linear processes.
It extends Kalman Filter which can only estimate linear processes by local linearization using Jacobians.
EKF SLAM is one of the simplest algorithms for SLAM problem.
It also gives quite good and accurate results.
Its main downside is quite high computational complexity.
Because for every update we must update a covariance matrix, which size depends on number of landmarks in the map, the complexity of O(N^2).
FastSLAM is an algorithm that was develop in order to create a solution that will be suitable for environments, where real-time computation is a must.
It estimates location of a robot using particles filter.
This allows for estimation of non-linear motion models.
Particles filter approach has one more big advantage.
Every particle can have its own map.
This way we can assume, during the observation update, that robot pose (for this particle) is known.
This way every landmark position is independent of other landmarks.
Therefore, we can store every landmark in separate 2x2 EKF filter, greatly reducing computational complexity during update.
Team decided to implement SLAM module using FastSLAM algorithm.
This is mostly dictated by need for an algorithm that will work in real-time parallel to other computationally expensive task running on ASMU’s computer.
With great complexity reduction comes only slight accuracy loss.
In some situations this accuracy loss might not even be the case.
Main disadvantage of FastSLAM 1.0 is neglecting observations in proposal distribution.
This means that during update there might be not enough particles that are close to real position.
This way we lose accuracy as well as particles will share same history much more often.
To fix this problem FastSLAM 2.0 was created.
It uses observations to get a better, more accurate proposal distribution.
This way it performs better than 1.0.
Especially when motion model is noisy.
The only draw back is little bit higher complexity and harder implementation.
To get best performance from SLAM module, the team decided to implement FastSLAM in version 2.0.
Basic implementation of FastSLAM 2.0 results in complexity of O(NM) where N is a number of particles and M is a number of landmarks in a map.
This can be improved with implementation of better data structures.
Firstly in order to reduce overall complexity we have to reduce complexity of data association.
With unknown data associations we have to implement a data structure that gives us great performance when accessing elements based on their position on the map.
K-D trees are such a structure.
They allow to access elements in k-dimensional space (in our case 2D) with average complexity of O(logN) where N is a number of elements in a tree.
Main problem with k-d trees is that there are hard to balance in changing environment.
When we are adding and deleting nodes from tree it can become unbalanced quite quickly.
We can combat that with even more complex data structures that are created on top of k-d trees, like for example BKD Trees.
In case of SLAM module, it was decided to stick with simple k-d trees as there was no time and real benefit to implement BKD trees (or other similar structures).
This is because of second way we will reduce FastSLAM complexity.
During resampling procedure with every particle that is copied we need to copy his whole map.
This is obviously not optimal as it takes a lot of time.
Because realistically most of landmarks of the map are not changed during update (only those in range of sensor) those can be shared between particles, that diverged from one given particle.
This can be implemented using smart pointers that will count how many particles (trees) are using given landmark, and when it is not needed anymore, it will be deleted.
When some particle wants to change, add or delete landmark, it will create a new path in its k-d tree containing new elements.
Because every time an landmark is changed, it must be first deleted and then inserted to the tree (as we cannot edit shared elements) the k-d tree should balance it self out.
Therefore implementation of BKD trees was abandoned.
For implementation of shared elements, C++’s smart pointers (std::shared_ptr) were used.
On desktop PC SLAM in debug build was consuming about 50% CPU (100% overall CPU consumption during that time).
While release build was consuming 3-5% of CPU.
There was no possibility of running SLAM in debug mode as it couldn’t run in real-time.
To fix the issue, profiler test were performed.
They showed that under debug, majority of time was spend in Eigen3 procedures.
The call stack over Eigen3 functionality was also very big.
n ordered to fix the issue, research about Eigen3 performance under debug configuration was performed.
This thread showed, that in debug build Eigen3 is using a lot of asserts and other debugging tools.
Those massively slow down the calculations.
To optimize Eigen3 performance under debug configuration, an -O2 flag was used. This optimization flag was only used for SLAM node, not for whole system build!
This fixed the problem and performance was similar to release configuration.
Improvement is also visible in profilers flame graph.
Unit testing.
In order to properly test k-d trees implementations for SLAM module, series of unit tests were implemented.
GTest framework was used as it is supported by ROS2.
Unit test were implemented for: K-d tree creation, insertion, deletion, nodes sharing between multiple trees, nearest neighbor search, rectangle range search, arc range search.
Multiple of those test were performed on generated datasets containing 1000, 10000 and 100000 points.
Unit test for other functionality than k-d trees wasn’t implemented as SLAM algorithms are highly probabilistic and modeling unit tests for those algorithms doesn’t make sense.
A test application was created in C++ in order to understand FastSLAM 1.0 algorithm.
The app was mocking data from randomly generated map and then SLAM was performed on this data.
Visualization was created using matplotlib for C++.
Application turned out to be successful.
It allowed for better understanding of FastSLAM before implementation in autonomous system.
SLAM pipeline testing was performed in Gazebo simulation.
In order to check if SLAM module is working correctly visualization was used.
RViz2 visualization shows: cones placement on the map (for best particle), localization of all particles, SLAM path history – [red colored path], odometry only path history – [purple colored path], real path history which is taken from simulation – [blue colored path], cones covariance, observation sensor range, observations.
For purpose of testing following sensors where simulated.
Camera perception: a special plugin to Gazebo simulation was created, that simulated perception from cameras, allowing for gaussian noise of angle and distance detection as well as simulated delay of perception data arrival.
IMU sensors with gaussian noise for motion estimation module.
GNSS sensor with gaussian noise for motion estimation module.
Odometry sensors with gaussian noise for motion estimation module."""
    spo_, svo_ = jr.execute(text)
    edge = []
    subj = []
    obj = []
    for s in spo_:
        if s.obj_attrs:
            for a in s.obj_attrs:
                subj.append(s.subj)
                edge.append(s.pred)
                obj.append(" ".join([s.obj, a]))
        else:
            subj.append(s.subj)
            edge.append(s.pred)
            obj.append(s.obj)

    subj1 = [s.subj for s in svo_]
    edge1 = [s.verb for s in svo_]
    obj1 = [s.obj for s in svo_]

    kg_df = pd.DataFrame({'subject': subj + subj1, 'object': obj + obj1, 'edge': edge1 + edge})

    G = nx.from_pandas_edgelist(kg_df, "subject", "object", edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G)
    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos=pos)
    nx.draw_networkx_edge_labels(G, pos=pos)
    plt.show()

