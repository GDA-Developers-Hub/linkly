"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/components/ui/use-toast"
import { Search, Send, MoreHorizontal, Phone, Video, ImageIcon, Paperclip, Smile } from "lucide-react"

// Mock data for development
const MOCK_CONVERSATIONS = [
  {
    id: 1,
    name: "Instagram Support",
    avatar: "/instagram-logo-on-phone.png",
    lastMessage: "We've reviewed your account and...",
    timestamp: "10:30 AM",
    unread: 2,
    platform: "instagram",
  },
  {
    id: 2,
    name: "Facebook Support",
    avatar: "/facebook-logo-display.png",
    lastMessage: "Your page insights for this week",
    timestamp: "Yesterday",
    unread: 0,
    platform: "facebook",
  },
  {
    id: 3,
    name: "Twitter Support",
    avatar: "/blue-bird-icon.png",
    lastMessage: "Your tweet has been approved",
    timestamp: "2 days ago",
    unread: 0,
    platform: "twitter",
  },
  {
    id: 4,
    name: "LinkedIn Support",
    avatar: "/linkedin-logo-on-white.png",
    lastMessage: "New connection request from...",
    timestamp: "3 days ago",
    unread: 0,
    platform: "linkedin",
  },
]

const MOCK_MESSAGES = [
  {
    id: 1,
    conversationId: 1,
    sender: "Instagram Support",
    senderAvatar: "/instagram-logo-on-phone.png",
    content: "Hello! How can we help you today?",
    timestamp: "10:15 AM",
    isMe: false,
  },
  {
    id: 2,
    conversationId: 1,
    sender: "Me",
    content: "Hi, I'm having trouble with my post scheduling. The posts aren't publishing at the scheduled time.",
    timestamp: "10:20 AM",
    isMe: true,
  },
  {
    id: 3,
    conversationId: 1,
    sender: "Instagram Support",
    senderAvatar: "/instagram-logo-on-phone.png",
    content: "I understand that can be frustrating. Let me check your account settings.",
    timestamp: "10:25 AM",
    isMe: false,
  },
  {
    id: 4,
    conversationId: 1,
    sender: "Instagram Support",
    senderAvatar: "/instagram-logo-on-phone.png",
    content:
      "We've reviewed your account and found that your API permissions need to be updated. We've fixed this issue for you.",
    timestamp: "10:30 AM",
    isMe: false,
  },
]

export default function MessagesPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [conversations, setConversations] = useState<any[]>([])
  const [messages, setMessages] = useState<any[]>([])
  const [selectedConversation, setSelectedConversation] = useState<any>(null)
  const [newMessage, setNewMessage] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true)
        // In a real app, we would fetch from the API
        // const api = getSocialBuAPI()
        // const conversationsData = await api.getConversations()

        // Using mock data for now
        setTimeout(() => {
          setConversations(MOCK_CONVERSATIONS)
          setMessages(MOCK_MESSAGES)
          setSelectedConversation(MOCK_CONVERSATIONS[0])
          setIsLoading(false)
        }, 1000)
      } catch (error) {
        console.error("Failed to load messages", error)
        toast({
          title: "Error",
          description: "Failed to load messages. Please try again.",
          variant: "destructive",
        })
        setIsLoading(false)
      }
    }

    loadData()
  }, [])

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedConversation) return

    const newMsg = {
      id: Math.floor(Math.random() * 1000) + 100,
      conversationId: selectedConversation.id,
      sender: "Me",
      content: newMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      isMe: true,
    }

    setMessages([...messages, newMsg])
    setNewMessage("")

    // Simulate response after 1 second
    setTimeout(() => {
      const responseMsg = {
        id: Math.floor(Math.random() * 1000) + 100,
        conversationId: selectedConversation.id,
        sender: selectedConversation.name,
        senderAvatar: selectedConversation.avatar,
        content: "Thanks for your message! Our team will get back to you shortly.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        isMe: false,
      }
      setMessages((prev) => [...prev, responseMsg])
    }, 1000)
  }

  const handleSelectConversation = (conversation: any) => {
    setSelectedConversation(conversation)

    // Mark as read
    setConversations(conversations.map((conv) => (conv.id === conversation.id ? { ...conv, unread: 0 } : conv)))
  }

  const filteredConversations = conversations.filter((conv) =>
    conv.name.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-[calc(100vh-10rem)]">
        <Card className="md:col-span-1">
          <CardHeader>
            <Skeleton className="h-8 w-32 mb-2" />
            <Skeleton className="h-10 w-full" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-full" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card className="md:col-span-2">
          <CardHeader>
            <Skeleton className="h-8 w-32" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className={`flex items-start space-x-2 ${i % 2 === 0 ? "" : "justify-end"}`}>
                  {i % 2 === 0 && <Skeleton className="h-10 w-10 rounded-full" />}
                  <Skeleton className={`h-20 ${i % 2 === 0 ? "w-2/3" : "w-1/2"} rounded-lg`} />
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Skeleton className="h-10 w-full" />
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-[calc(100vh-10rem)]">
      <Card className="md:col-span-1 flex flex-col">
        <CardHeader>
          <CardTitle>Messages</CardTitle>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search conversations..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-[calc(100vh-16rem)]">
            <div className="space-y-2">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`flex items-center space-x-4 p-3 rounded-lg cursor-pointer ${
                    selectedConversation?.id === conversation.id ? "bg-muted" : "hover:bg-muted/50"
                  }`}
                  onClick={() => handleSelectConversation(conversation)}
                >
                  <Avatar>
                    <AvatarImage src={conversation.avatar || "/placeholder.svg"} alt={conversation.name} />
                    <AvatarFallback>{conversation.name[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="font-medium truncate">{conversation.name}</p>
                      <span className="text-xs text-muted-foreground">{conversation.timestamp}</span>
                    </div>
                    <p className="text-sm text-muted-foreground truncate">{conversation.lastMessage}</p>
                  </div>
                  {conversation.unread > 0 && <Badge className="ml-auto">{conversation.unread}</Badge>}
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 flex flex-col">
        {selectedConversation ? (
          <>
            <CardHeader className="flex flex-row items-center border-b p-4">
              <div className="flex items-center flex-1">
                <Avatar className="h-10 w-10 mr-4">
                  <AvatarImage
                    src={selectedConversation.avatar || "/placeholder.svg"}
                    alt={selectedConversation.name}
                  />
                  <AvatarFallback>{selectedConversation.name[0]}</AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-lg">{selectedConversation.name}</CardTitle>
                  <CardDescription>
                    <Badge variant="outline" className="capitalize">
                      {selectedConversation.platform}
                    </Badge>
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="icon">
                  <Phone className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Video className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-4">
              <ScrollArea className="h-[calc(100vh-22rem)]">
                <div className="space-y-4">
                  {messages
                    .filter((msg) => msg.conversationId === selectedConversation.id)
                    .map((message) => (
                      <div key={message.id} className={`flex ${message.isMe ? "justify-end" : "justify-start"}`}>
                        <div className="flex items-start max-w-[80%] space-x-2">
                          {!message.isMe && (
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={message.senderAvatar || "/placeholder.svg"} alt={message.sender} />
                              <AvatarFallback>{message.sender[0]}</AvatarFallback>
                            </Avatar>
                          )}
                          <div>
                            <div
                              className={`rounded-lg p-3 ${
                                message.isMe ? "bg-primary text-primary-foreground" : "bg-muted"
                              }`}
                            >
                              <p>{message.content}</p>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">{message.timestamp}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            </CardContent>
            <CardFooter className="border-t p-4">
              <div className="flex items-center w-full space-x-2">
                <Button variant="ghost" size="icon">
                  <Paperclip className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <ImageIcon className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Smile className="h-4 w-4" />
                </Button>
                <Input
                  placeholder="Type a message..."
                  className="flex-1"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSendMessage()
                    }
                  }}
                />
                <Button onClick={handleSendMessage} disabled={!newMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardFooter>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h3 className="text-lg font-medium">No conversation selected</h3>
              <p className="text-muted-foreground">Select a conversation from the list to start messaging</p>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
