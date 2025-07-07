---
layout: post
title: "Meet areq: Async Python Requests Without Losing Your Sanity"
publish: true
---

<!-- # Meet areq: Async Python Requests Without Losing Your Sanity -->
If you’ve written Python scripts that use requests, you know how intuitive and reliable it feels. It just works. It’s simple. And it’s become almost muscle memory at this point.

The story starts with a simple piece of code that looks something like this.

```python
import requests

def foo():
	try:
		response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
		assert isinstance(response, requests.Response)
		response.raise_for_status()
		if response.ok:
			response_json = response.json()
			return response_json
	except requests.exceptions.RequestException as e:
		response_text = response.text
        print("Text:", response_text)
        return None

if __name__ == '__main__':
	foo()
```

It’s clean, concise, easily testable.

But then your application grows. Maybe you’re hitting hundreds of APIs, or building a web scraper. Anyway, your trusty synchronous code is no longer snappy. It starts to slow down. And someone suggests why not go async? The idea sticks in your head. It seems elegant, beautiful and most of all, inevitable. 

So, you start the refactor.  You read up about `httpx`, the de-facto library for anyone wanting to make async requests. And it does seem simple - at first. But after refactoring and debugging, you are left with this.
```python
import httpx
import asyncio

async def foo():
	try:
		async with httpx.AsyncClient() as client:
			response = await client.get("https://jsonplaceholder.typicode.com/todos/1")
			assert isinstance(response, httpx.Response)
			response.raise_for_status()
			if response.is_success:
				response_json = response.json()
				print(response_json)
	except httpx.HTTPError as e:
		print("Text:", getattr(response, 'text', None))
		return None

if __name__ == "__main__":
	asyncio.run(foo())


```
Great. You have joined the async revolution. But something feels weird. So many changes just to get the async flow to work!
- httpx.AsyncClient() context manager
- client.get() returns a coroutine that must be awaited
- exceptions raised are no longer `requests.exceptions.RequestException`
- response.ok is now response.is_success

From a refactoring point of view, I am definitely more nervous and less confident about the `httpx` code than the `requests` code. Not because `httpx` is a bad library, but because the affected area is a lot. If something goes wrong, it is going to be very hard to debug. Plus, I no longer recognize the code or the idioms.

This was exactly the problem I was trying to solve. An elegant way to move from synchronous workflows using requests to asynchronous workflows using `httpx` in an elegant way. 

This led me to build `areq`: a minimal async drop-in replacement for requests—no weird new interfaces, no extra ceremony. Just async where you want it, and familiar behavior where you expect it. Here’s the same code using areq instead of requests—with almost nothing changed.
```python
import areq
import asyncio
import requests

async def foo():
	try:
		response = await areq.get("https://jsonplaceholder.typicode.com/todos/1")
		assert isinstance(response, requests.Response)
		response.raise_for_status()
		if response.ok:
			response_json = response.json()
			print(response_json)
	except requests.exceptions.RequestException as e:
		print("Text:", getattr(response, 'text', None))
		return None

if __name__ == "__main__":
	asyncio.run(foo())
```

That’s it. No extra configs, no new types to learn. No special idioms. Sure, I had to add async-await wherever required. But almost nothing else has changed. What’s more,  `isinstance(response, requests.Response)` returns True!
- No boilerplate context managers
- No new Response object to learn
- Type checks and except clauses remain same

## Who did I build for?
The goal behind `areq` is simple: Bring async benefits to your software without wrecking your code (or your brain). You get your requests ergonomics plus async speed—no rewrites, no API mental overhead. 
`areq` is nothing fancy: it is just a simple wrapper over httpx. But I feel it will be really useful for some people.

### 🔄 Teams migrating to async gradually
You don’t always have the luxury to stop everything and refactor your entire codebase for async. With `areq`, you can start adopting async piece by piece, keeping the rest of your logic intact.

Want to convert just one function? One endpoint? One module?
`areq` enables you to do just that, without breaking .ok, type assertions or your test mocks.

### 🧠 People who eventually want to move to `httpx` (but not today)

`areq` isn’t here to compete with `httpx`.
In fact, it can be your on-ramp to `httpx`.

You can use `areq` to unlock async performance now—without rewriting everything. Later, once you’ve stabilized your logic and gathered profiling data, you can move to native `httpx` for deeper control or streaming needs.

### 🧵 Builders of CLI tools, background jobs, and lightweight APIs
If you’re working on scrapers, bots, micro services or any software that needs concurrency but don’t want the full mental load of switching to a new request paradigm, `areq` is for you. It gives you async without ceremony.

### 💼 Teams maintaining legacy requests code
Your old requests code works fine. It’s battle-tested.
Now you just want it to go faster.
`areq` lets you do that.
No rewrite. No breakage. No angry regression tests.

## Try it now!
### 1. Install it
Open your terminal, choose your favorite new python virtual env.
Run the follwing command
```
pip install areq
```

### 2. Try it in your script
```
import areq

response = await areq.get("https://httpbin.org/get")
print(response.status_code)
```

## What’s Under the Hood?
`areq`:
- Uses `httpx.AsyncClient` under the hood.
- Converts the response to a requests.Response lookalike.
- Converts common `httpx` exceptions (e.g. `httpx.ConnectTimeout`) into `requests.exceptions.RequestException` subclasses.
- Supports all basic HTTP verbs

It’s not a full replacement for everything `httpx` or `requests` can do, but it covers 90% of practical use cases, especially when you’re trying to modernize an old codebase.

### Known Limitations
- Streaming and advanced session handling are not supported (yet!)
- The response object is a subclass of `requests.Response`, but cannot be treated as same in all scenarios.
But hey—it’s early. And it works for most real-world use cases.

## Installing and Using `areq`
It is very easy to install `areq`. You can install it from PyPi just like any other python package.

`pip install areq`


## How You Can Help
### Star the [repo](https://github.com/ganesh-palanikumar/areq)
Starring the repo helps more people discover `areq`, and lets you keep up to date with features as they roll out.
### Use it in your code!
Take `areq` for a spin. Use it in your code, tell me what breaks. File an [issue](https://github.com/ganesh-palanikumar/areq/issues).
### Suggest features
Want streaming support? Cookie handling? What is that one feature that will make your life so much better?
### Contribute!
`areq` is open sourced under MIT license. It is also my project with me as the sole developer. As such, if you have a cool idea, do fork the repository, implement and put up a PR. I will definitely review it.
### Spread the word
Tell your friends and colleagues. Blog about it - the good, the bad and the ugly. The more people who use `areq`, the better it is going to become. 

## Final Thoughts
Sometimes all you need is a small wrapper that respects your old habits.
That’s `areq`. It won’t save the world, but it’ll save you a few afternoons.

If you’ve ever:
- wanted to “just make it async” without rewriting everything
- been burned by subtle differences between `requests` and `httpx`
- Or you just want to make your trusty legacy code run a bit faster

Then `areq` might just be your new favorite micro-library.
