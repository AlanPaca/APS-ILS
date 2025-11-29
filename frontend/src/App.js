import { useState, useEffect, useRef } from 'react';
import '@/App.css';
import axios from 'axios';
import { Send, Sparkles, Tag, Trash2, Search, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [storeContent, setStoreContent] = useState('');
  const [entries, setEntries] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchEntries();
    fetchTags();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchEntries = async (tag = null) => {
    try {
      const url = tag ? `${API}/entries?tag=${encodeURIComponent(tag)}` : `${API}/entries`;
      const response = await axios.get(url);
      setEntries(response.data);
    } catch (error) {
      console.error('Error fetching entries:', error);
      toast.error('Failed to fetch entries');
    }
  };

  const fetchTags = async () => {
    try {
      const response = await axios.get(`${API}/tags`);
      setAllTags(response.data);
    } catch (error) {
      console.error('Error fetching tags:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: userMessage,
        session_id: sessionId
      });
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error(error.response?.data?.detail || 'Failed to send message. Please check if API key is configured.');
      // Keep user message visible even if AI response fails
    } finally {
      setIsLoading(false);
    }
  };

  const storeEntry = async () => {
    if (!storeContent.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/store`, {
        content: storeContent
      });
      toast.success('Content stored with AI-generated tags!');
      setStoreContent('');
      await fetchEntries(selectedTag);
      await fetchTags();
    } catch (error) {
      console.error('Error storing entry:', error);
      toast.error(error.response?.data?.detail || 'Failed to store content');
      setStoreContent(''); // Clear textarea even on error for better UX
    } finally {
      setIsLoading(false);
    }
  };

  const deleteEntry = async (entryId) => {
    try {
      await axios.delete(`${API}/entries/${entryId}`);
      toast.success('Entry deleted');
      await fetchEntries(selectedTag);
      await fetchTags();
    } catch (error) {
      console.error('Error deleting entry:', error);
      toast.error('Failed to delete entry');
    }
  };

  const handleTagClick = (tag) => {
    if (selectedTag === tag) {
      setSelectedTag(null);
      fetchEntries();
    } else {
      setSelectedTag(tag);
      fetchEntries(tag);
    }
  };

  const filteredEntries = entries.filter(entry => 
    entry.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const tagColors = [
    { bg: 'bg-green-100', text: 'text-green-900' },
    { bg: 'bg-blue-100', text: 'text-blue-900' },
    { bg: 'bg-yellow-100', text: 'text-yellow-900' },
    { bg: 'bg-purple-100', text: 'text-purple-900' },
    { bg: 'bg-rose-100', text: 'text-rose-900' }
  ];

  const getTagColor = (index) => tagColors[index % tagColors.length];

  return (
    <div className="h-screen w-full flex overflow-hidden bg-background">
      <Toaster position="top-center" />
      
      {/* Sidebar - Stored Entries */}
      <div className="w-80 flex-shrink-0 border-r border-border bg-surface hidden md:flex flex-col">
        <div className="p-6 border-b border-border">
          <h2 className="text-xl font-semibold text-primary flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Stored Information
          </h2>
          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              data-testid="search-entries-input"
              placeholder="Search entries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {/* Tags Filter */}
        {allTags.length > 0 && (
          <div className="p-4 border-b border-border">
            <p className="text-sm font-medium mb-2 text-foreground">Filter by Tag:</p>
            <div className="flex flex-wrap gap-2">
              {allTags.map((tag, index) => {
                const colors = getTagColor(index);
                return (
                  <Badge
                    key={tag}
                    data-testid={`filter-tag-${tag}`}
                    onClick={() => handleTagClick(tag)}
                    className={`cursor-pointer transition-all ${colors.bg} ${colors.text} ${selectedTag === tag ? 'ring-2 ring-primary' : ''}`}
                  >
                    {tag}
                  </Badge>
                );
              })}
            </div>
          </div>
        )}

        {/* Entries List */}
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-3">
            {filteredEntries.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No entries yet. Store some content to get started!
              </p>
            ) : (
              filteredEntries.map((entry, index) => {
                const colors = getTagColor(index);
                return (
                  <div
                    key={entry.id}
                    data-testid={`stored-entry-${index}`}
                    className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 hover:shadow-sm transition-all duration-200"
                  >
                    <p className="text-sm text-foreground mb-2 line-clamp-3">{entry.content}</p>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {entry.tags.map((tag) => {
                        const tagIndex = allTags.indexOf(tag);
                        const tagColors = getTagColor(tagIndex);
                        return (
                          <Badge
                            key={tag}
                            data-testid={`entry-tag-${tag}`}
                            className={`text-xs ${tagColors.bg} ${tagColors.text}`}
                          >
                            {tag}
                          </Badge>
                        );
                      })}
                    </div>
                    <div className="flex justify-between items-center text-xs text-muted-foreground">
                      <span>{new Date(entry.created_at).toLocaleDateString()}</span>
                      <Button
                        data-testid={`delete-entry-${index}`}
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteEntry(entry.id)}
                        className="h-6 w-6 p-0 hover:text-red-600"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="p-6 border-b border-border bg-white/80 backdrop-blur-xl">
          <h1 className="text-3xl font-bold text-primary tracking-tight">APS Job Application Helper</h1>
          <p className="text-sm text-muted-foreground mt-1">Expert assistance with Australian Public Service ILS applications</p>
        </div>

        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-accent/10 mb-4">
                  <Sparkles className="h-8 w-8 text-accent" />
                </div>
                <h2 className="text-2xl font-semibold text-primary mb-2">Welcome to APS Job Helper</h2>
                <p className="text-muted-foreground max-w-md mx-auto">
                  Ask me anything about APS ILS competencies, selection criteria, or get help crafting your job application responses.
                </p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  data-testid={`chat-message-${msg.role}-${index}`}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-2xl rounded-tr-sm'
                        : 'bg-surface border border-border text-foreground rounded-2xl rounded-tl-sm shadow-sm'
                    } px-5 py-3`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-surface border border-border rounded-2xl rounded-tl-sm px-5 py-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="p-6 border-t border-border bg-white/80 backdrop-blur-xl">
          <div className="max-w-4xl mx-auto space-y-4">
            {/* Chat Input */}
            <form onSubmit={sendMessage} className="flex gap-2">
              <Input
                data-testid="chat-input"
                placeholder="Ask about APS ILS competencies, selection criteria..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                data-testid="send-message-button"
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="bg-primary hover:bg-primary/90"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>

            {/* Store Content */}
            <div className="border border-border rounded-lg p-4 bg-surface">
              <div className="flex items-center gap-2 mb-2">
                <Tag className="h-4 w-4 text-accent" />
                <p className="text-sm font-medium text-foreground">Store & Tag Information</p>
              </div>
              <div className="flex gap-2">
                <Textarea
                  data-testid="store-content-textarea"
                  placeholder="Paste your selection criteria response, resume points, or other content. AI will analyze and tag it automatically."
                  value={storeContent}
                  onChange={(e) => setStoreContent(e.target.value)}
                  disabled={isLoading}
                  className="flex-1 min-h-[80px]"
                />
                <Button
                  data-testid="store-content-button"
                  onClick={storeEntry}
                  disabled={isLoading || !storeContent.trim()}
                  className="self-end bg-accent hover:bg-accent/90 text-white"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Store
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;