//
// Copied from a stack overflow thread:
// https://stackoverflow.com/questions/15278343/c11-thread-safe-queue
// Should improve this later for our specific use case later.
//

#ifndef SOFTWARE_SAFE_QUEUE_HPP
#define SOFTWARE_SAFE_QUEUE_HPP

#include <queue>
#include <mutex>
#include <condition_variable>

template <class T>
class safe_queue {
    public:
        T null_item;

        safe_queue(T null_item)
                : q()
                , m()
                , c()
        {
            this->null_item = null_item;
        }

        ~safe_queue(void)
        {}

        // Add an element to the queue.
        void enqueue(T t)
        {
            std::lock_guard<std::mutex> lock(m);
            q.push(t);
            c.notify_one();
        }

        // Get the "front"-element.
        // If the queue is empty, wait till a element is avaiable.
        T dequeue(void)
        {
            std::unique_lock<std::mutex> lock(m);
            while(q.empty())
            {
                // release lock as long as the wait and reaquire it afterwards.
                c.wait(lock);
            }
            T val = q.front();
            q.pop();
            return val;
        }

        // Get the "front"-element.
        // If the queue is empty, return the null item we got during initialization.
        T poll(void)
        {
            std::unique_lock<std::mutex> lock(m);
            if (q.empty()) {
                /*
                 * Return immediately with the null item instead of waiting for a new insert.
                 */
                return this->null_item;
            }
            T val = q.front();
            q.pop();
            return val;
        }

    private:
        std::queue<T> q;
        mutable std::mutex m;
        std::condition_variable c;


};


#endif //SOFTWARE_SAFE_QUEUE_HPP
