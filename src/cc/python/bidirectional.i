/* File : bidirectional.i */

%module(directors="1") bidirectional
%{
#include "bidirectional.h"
#include "py_ref_callback.h"
using namespace bidirectional;
%}

/* Type templates */
%include <std_vector.i>
%include <std_string.i>

%template(DoubleVector) std::vector<double>;
%template(StringVector) std::vector<std::string>;

/* turn on director wrapping Callback */
%feature("director") bidirectional::PyREFCallback;

%rename($ignore, %$isclass) "";
%rename("%s") bidirectional;
%rename(BiDirectionalCpp) bidirectional::BiDirectional;
%rename("%s") bidirectional::BiDirectional::BiDirectional;
%rename("%s") bidirectional::BiDirectional::~BiDirectional;
/* Expose graph construction and setters */
%rename("%s") bidirectional::BiDirectional::addEdge;
%rename("%s") bidirectional::BiDirectional::setPyCallback;
%rename("%s") bidirectional::BiDirectional::setSeed;
/* Expose all solving members */
%rename("%s") bidirectional::BiDirectional::direction;
%rename("%s") bidirectional::BiDirectional::method;
%rename("%s") bidirectional::BiDirectional::time_limit;
%rename("%s") bidirectional::BiDirectional::threshold;
%rename("%s") bidirectional::BiDirectional::elementary;
%rename("%s") bidirectional::BiDirectional::dominance_frequency;
/* Expose getters */
%rename("%s") bidirectional::BiDirectional::getPath;
%rename("%s") bidirectional::BiDirectional::getTotalCost;
%rename("%s") bidirectional::BiDirectional::getConsumedResources;

%rename("%s") bidirectional::PyREFCallback;
%rename("%s") bidirectional::PyREFCallback::PyREFCallback;
%rename("%s") bidirectional::PyREFCallback::~PyREFCallback;
%rename("%s") bidirectional::PyREFCallback::REF_fwd;
%rename("%s") bidirectional::PyREFCallback::REF_bwd;
%rename("%s") bidirectional::PyREFCallback::REF_join;

%include "bidirectional.h"
%include "py_ref_callback.h"
