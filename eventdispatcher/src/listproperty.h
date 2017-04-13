#ifndef LISTPROPERTY_INCLUDED
#define LISTPROPERTY_INCLUDED

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>

#include "eventdispatcher.h"
#include "property.h"

namespace bp = boost::python;

// Create a pointer to the dispatching method
typedef void (cProperty::*dispatch_method)(cEventDispatcher, bp::list);


class cObservableList {

    public:
        bp::list list;
        cProperty* property;
        cObservableList(bp::list l, cProperty* property){
                this->list = l;
                this->property = property;
            };


};



class cListProperty : public cProperty {

    public:

        cListProperty(bp::object obj) : cProperty(obj) {};

        template <typename T> void __set__(cEventDispatcher obj, T value);

        void register_property(cEventDispatcher instance, const char* property_name, bp::list default_value) {
//            void (cProperty::*_dispatcher)(cEventDispatcher, bp::list) = &cProperty::dispatch<bp::list>;
//            void (*_dispatcher)(bp::list);
//            dispatch_method _dispatcher = cProperty::dispatch<cEventDispatcher, bp::list>;
//            dispatch_method _dispatcher = &cProperty::dispatch<cEventDispatcher, bp::list>;
            cObservableList obs_list = cObservableList(default_value, this);

            cProperty::register_property(instance, property_name, default_value);
            instance.event_dispatcher_properties[property_name]["value"] = bp::object(obs_list);
        }

};



#endif // LISTPROPERTY_INCLUDED
