/* File : bidirectional.i */

%include "base.i"

%module(directors="1") bidirectional
%{
#include "bidirectional.h"
#include "ref_callback.h"
using namespace bidirectional;
%}

/* Type templates */
%include <std_string.i>
%include <std_vector.i>

%template(DoubleVector) std::vector<double>;
%template(IntVector) std::vector<int>;

/* turn on director wrapping REFCallback */
%feature("director") bidirectional::REFCallback;

/* %feature("director:except") {
  if ($error != NULL) {
    throw Swig::DirectorMethodException();
  }
}
%exception {
  try { $action }
  catch (Swig::DirectorException &e) { SWIG_fail; }
} */


%rename($ignore, %$isclass) "";
%rename("%s") bidirectional;
/* Expose constructor */
%rename(BiDirectionalCpp) bidirectional::BiDirectional;
%rename("%s") bidirectional::BiDirectional::BiDirectional;
%rename("%s") bidirectional::BiDirectional::~BiDirectional;
/* Expose graph construction */
%rename("%s") bidirectional::BiDirectional::addNodes;
%rename("%s") bidirectional::BiDirectional::addEdge;
/* Expose algorithm parameters setters */
%rename("%s") bidirectional::BiDirectional::setDirection;
%rename("%s") bidirectional::BiDirectional::setMethod;
%rename("%s") bidirectional::BiDirectional::setTimeLimit;
%rename("%s") bidirectional::BiDirectional::setThreshold;
%rename("%s") bidirectional::BiDirectional::setElementary;
%rename("%s") bidirectional::BiDirectional::setBoundsPruning;
%rename("%s") bidirectional::BiDirectional::setFindCriticalRes;
%rename("%s") bidirectional::BiDirectional::setCriticalRes;
%rename("%s") bidirectional::BiDirectional::setREFCallback;
%rename("%s") bidirectional::BiDirectional::setTwoCycleElimination;
/* Expose getters */
%rename("%s") bidirectional::BiDirectional::getPath;
%rename("%s") bidirectional::BiDirectional::getTotalCost;
%rename("%s") bidirectional::BiDirectional::getConsumedResources;
%rename("%s") bidirectional::BiDirectional::checkCriticalRes;

/* Expose methods of REFCallback */
%rename("%s") bidirectional::REFCallback;
%rename("%s") bidirectional::REFCallback::REFCallback;
%rename("%s") bidirectional::REFCallback::~REFCallback;
%rename("%s") bidirectional::REFCallback::REF_fwd;
%rename("%s") bidirectional::REFCallback::REF_bwd;
%rename("%s") bidirectional::REFCallback::REF_join;

%include "bidirectional.h"
%include "ref_callback.h"
