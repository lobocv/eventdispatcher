#ifndef EVENTDISPATCHER_INCLUDED
#define EVENTDISPATCHER_INCLUDED

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>


namespace bp = boost::python;



class cEventDispatcher : public bp::object {

    public:
        bp::dict event_dispatcher_properties;
        bp::list event_dispatcher_event_callbacks;

        cEventDispatcher();

        void dispatch();
};


#endif // EVENTDISPATCHER_INCLUDED
