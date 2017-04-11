#ifndef LISTPROPERTY_INCLUDED
#define LISTPROPERTY_INCLUDED

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>

#include "property.h"

namespace bp = boost::python;


class cListProperty : public cProperty {

    public:

        cListProperty(bp::object obj) : cProperty(obj) {};

        template <typename T> void __set__(cEventDispatcher obj, T value);

};


#endif // LISTPROPERTY_INCLUDED
