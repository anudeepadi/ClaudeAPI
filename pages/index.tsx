import type { NextPage } from 'next'
import Head from 'next/head'
import { useState, useEffect } from 'react'

const Home: NextPage = () => {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')

  return (
    <>
      <Head>
        <title>ClaudeAPI</title>
        <meta name="description" content="Claude API Integration" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900">
              ClaudeAPI
            </h1>
            <p className="mt-4 text-xl text-gray-600">
              Your Claude.ai API integration
            </p>
          </div>

          <div className="max-w-2xl mx-auto">
            <form className="space-y-4">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full h-32 p-4 border rounded-md"
                placeholder="Enter your message..."
              />
              <button
                type="submit"
                className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Send Message
              </button>
            </form>

            {response && (
              <div className="mt-8">
                <h2 className="text-xl font-semibold mb-4">Response:</h2>
                <div className="p-4 bg-white rounded-md shadow">
                  {response}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export default Home