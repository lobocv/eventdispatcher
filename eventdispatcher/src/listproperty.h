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
        cEventDispatcher eventdispatcher;

        cObservableList(bp::list l, cEventDispatcher dispatcher, cProperty* property){
                this->list = l;
                this->property = property;
                this->eventdispatcher = dispatcher;
            };

        bp::list __get__(cEventDispatcher obj, bp::object asd) {
            return this->list;
        }

        void append(bp::object item) {
            this->list.append(item);
            (this->property)->dispatch(this->eventdispatcher, this->list);
        }

        template <typename T> void extend(T items) {
            this->list.extend(items);
            (this->property)->dispatch(this->eventdispatcher, this->list);
        }

        void insert(int index, bp::object item) {
            this->list.insert(index, item);
            (this->property)->dispatch(this->eventdispatcher, this->list);
        }

        bp::object pop(){
            bp::object last_item = this->list.pop();
            (this->property)->dispatch(this->eventdispatcher, this->list);
            return last_item;
        }

        int __len__(){
            return len(this->list);
        }

        bool __eq__(bp::object other){
            return this->list == other;
        }

        bool __neq__(bp::object other){
            return this->list != other;
        }

        bool __nonzero__() {
            return len(this->list) > 0;
        }


};



class cListProperty : public cProperty {

    public:

        cListProperty(bp::object obj) : cProperty(obj) {};

        template <typename T> void __set__(cEventDispatcher obj, T value);

        void register_property(cEventDispatcher instance, const char* property_name, bp::list default_value) {
            // Create a new list for each instance
            bp::list copied_list = bp::list();
            for (int i=0; i<len(default_value); i++){
                copied_list.append(default_value[i]);
            }

            cObservableList obs_list = cObservableList(copied_list, instance, this);

            cProperty::register_property(instance, property_name, copied_list);
            // Override the references to point to the ListProperty and ObservableList
            instance.event_dispatcher_properties[property_name]["property"] = this;
            instance.event_dispatcher_properties[property_name]["value"] = bp::object(obs_list);
        }

};



#endif // LISTPROPERTY_INCLUDED
