/* File : bidirectional.i */

%module(directors="1") bidirectional
%{
#include "bidirectional.h"
#include "ref_callback.h"
using namespace bidirectional;
%}

/* Type templates */
%include <std_vector.i>
%include <std_string.i>

%template(DoubleVector) std::vector<double>;
/* Needed for graph, ow causes memory leak */
%template(StringVector) std::vector<std::string>;
%template(IntVector) std::vector<int>;

/* turn on director wrapping Callback */
%feature("director") bidirectional::REFCallback;

%rename($ignore, %$isclass) "";
%rename("%s") bidirectional;
%rename(BiDirectionalCpp) bidirectional::BiDirectional;
%rename("%s") bidirectional::BiDirectional::BiDirectional;
%rename("%s") bidirectional::BiDirectional::~BiDirectional;
/* Expose algorithm parameters */
%rename("%s") bidirectional::SolvingOptions;
%rename("%s") bidirectional::BiDirectional::options;
/* Expose graph construction and setters */
%rename("%s") bidirectional::BiDirectional::addNodes;
%rename("%s") bidirectional::BiDirectional::addEdge;
%rename("%s") bidirectional::BiDirectional::setREFCallback;
/* Expose getters */
%rename("%s") bidirectional::BiDirectional::getPath;
%rename("%s") bidirectional::BiDirectional::getTotalCost;
%rename("%s") bidirectional::BiDirectional::getConsumedResources;

%rename("%s") bidirectional::REFCallback;
%rename("%s") bidirectional::REFCallback::REFCallback;
%rename("%s") bidirectional::REFCallback::~REFCallback;
%rename("%s") bidirectional::REFCallback::REF_fwd;
%rename("%s") bidirectional::REFCallback::REF_bwd;
%rename("%s") bidirectional::REFCallback::REF_join;

%include "bidirectional.h"
%include "ref_callback.h"
