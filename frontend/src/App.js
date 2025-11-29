import { useState, useEffect, useRef } from 'react';
import '@/App.css';
import axios from 'axios';
import { Send, Plus, Search, Filter, Edit2, Trash2, Save, X, FileText, Sparkles, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const APS_LEVELS = ['APS1', 'APS2', 'APS3', 'APS4', 'APS5', 'APS6', 'EL1', 'EL2'];
const ILS_CAPABILITIES = [
  'Supports Strategic Direction',
  'Achieves Results',
  'Supports Productive Working Relationships',
  'Displays Personal Drive and Integrity',
  'Communicates with Influence'
];

function App() {
  const [examples, setExamples] = useState([]);
  const [filteredExamples, setFilteredExamples] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedExample, setSelectedExample] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [assessmentText, setAssessmentText] = useState('');
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [isAssessing, setIsAssessing] = useState(false);
  const [filterOptions, setFilterOptions] = useState({ capabilities: [], behaviours: [], tags: [], aps_levels: [] });
  const [activeFilters, setActiveFilters] = useState({ aps_level: '', capability: '', tag: '' });
  const assessmentEndRef = useRef(null);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    example_text: '',
    role: '',
    aps_level: 'APS6',
    capabilities: [],
    behaviours: [],
    tags: []
  });

  useEffect(() => {
    fetchExamples();
    fetchFilterOptions();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [examples, searchQuery, activeFilters]);

  useEffect(() => {
    assessmentEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [assessmentResult]);

  const fetchExamples = async () => {
    try {
      const response = await axios.get(`${API}/work-examples`);
      setExamples(response.data);
    } catch (error) {
      console.error('Error fetching examples:', error);
      toast.error('Failed to fetch work examples');
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await axios.get(`${API}/filters`);
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...examples];

    if (searchQuery) {
      filtered = filtered.filter(ex => 
        ex.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ex.example_text.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (activeFilters.aps_level) {
      filtered = filtered.filter(ex => ex.aps_level === activeFilters.aps_level);
    }

    if (activeFilters.capability) {
      filtered = filtered.filter(ex => ex.capabilities.includes(activeFilters.capability));
    }

    if (activeFilters.tag) {
      filtered = filtered.filter(ex => ex.tags.includes(activeFilters.tag));
    }

    setFilteredExamples(filtered);
  };

  const handleSubmitExample = async (e) => {
    e.preventDefault();
    try {
      if (selectedExample) {
        await axios.put(`${API}/work-examples/${selectedExample.id}`, formData);
        toast.success('Work example updated!');
      } else {
        await axios.post(`${API}/work-examples`, formData);
        toast.success('Work example added!');
      }
      resetForm();
      fetchExamples();
      fetchFilterOptions();
    } catch (error) {
      console.error('Error saving example:', error);
      toast.error(error.response?.data?.detail || 'Failed to save example');
    }
  };

  const handleDeleteExample = async (id) => {
    if (!window.confirm('Are you sure you want to delete this example?')) return;
    
    try {
      await axios.delete(`${API}/work-examples/${id}`);
      toast.success('Example deleted');
      fetchExamples();
      fetchFilterOptions();
    } catch (error) {
      console.error('Error deleting example:', error);
      toast.error('Failed to delete example');
    }
  };

  const handleAssess = async () => {
    if (!assessmentText.trim() || isAssessing) return;

    setIsAssessing(true);
    setAssessmentResult(null);

    try {
      const response = await axios.post(`${API}/assess`, {
        example_text: assessmentText,
        aps_level: 'APS6'
      });
      setAssessmentResult(response.data.assessment);
    } catch (error) {
      console.error('Error assessing:', error);
      toast.error(error.response?.data?.detail || 'Assessment failed. Please check if API key is configured.');
    } finally {
      setIsAssessing(false);
    }
  };

  const handleSaveAssessment = async () => {
    if (!assessmentResult) return;

    try {
      await axios.post(`${API}/assessments/save`, {
        example_text: assessmentText,
        assessment_text: assessmentResult,
        example_id: selectedExample?.id
      });
      toast.success('Assessment saved!');
    } catch (error) {
      console.error('Error saving assessment:', error);
      toast.error('Failed to save assessment');
    }
  };

  const handleEditExample = (example) => {
    setSelectedExample(example);
    setFormData({
      title: example.title,
      example_text: example.example_text,
      role: example.role,
      aps_level: example.aps_level,
      capabilities: example.capabilities,
      behaviours: example.behaviours,
      tags: example.tags
    });
    setShowAddForm(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      example_text: '',
      role: '',
      aps_level: 'APS6',
      capabilities: [],
      behaviours: [],
      tags: []
    });
    setSelectedExample(null);
    setShowAddForm(false);
  };

  const handleArrayInput = (field, value) => {
    const items = value.split(',').map(item => item.trim()).filter(item => item);
    setFormData(prev => ({ ...prev, [field]: items }));
  };

  const handleUseExample = (example) => {
    setAssessmentText(example.example_text);
  };

  return (
    <div className="h-screen w-full flex flex-col overflow-hidden bg-background">
      <Toaster position="top-center" />
      
      {/* Header */}
      <div className="px-4 md:px-6 py-3 md:py-4 border-b border-border bg-white">
        <h1 className="text-xl md:text-3xl font-bold text-primary tracking-tight">APS ILS Work Examples Manager</h1>
        <p className="text-xs md:text-sm text-muted-foreground mt-1">Manage and assess work examples against APS Integrated Leadership System</p>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Left Sidebar - Work Examples */}
        <div className="w-full md:w-96 flex-shrink-0 md:border-r border-b md:border-b-0 border-border bg-surface flex flex-col max-h-[40vh] md:max-h-none">
          <div className="p-3 md:p-4 border-b border-border">
            <div className="flex gap-2 mb-3">
              <Button
                data-testid="add-example-button"
                onClick={() => setShowAddForm(true)}
                className="flex-1 bg-primary hover:bg-primary/90"
                size="sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Example
              </Button>
            </div>
            
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                data-testid="search-examples-input"
                placeholder="Search examples..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            <div className="space-y-2">
              <Select value={activeFilters.aps_level || undefined} onValueChange={(val) => setActiveFilters(prev => ({ ...prev, aps_level: val === 'all' ? '' : val }))}>
                <SelectTrigger data-testid="filter-aps-level">
                  <SelectValue placeholder="Filter by APS Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  {APS_LEVELS.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={activeFilters.capability || undefined} onValueChange={(val) => setActiveFilters(prev => ({ ...prev, capability: val === 'all' ? '' : val }))}>
                <SelectTrigger data-testid="filter-capability">
                  <SelectValue placeholder="Filter by Capability" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Capabilities</SelectItem>
                  {ILS_CAPABILITIES.map(cap => (
                    <SelectItem key={cap} value={cap}>{cap}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <ScrollArea className="flex-1">
            <div className="p-4 space-y-3">
              {filteredExamples.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  {searchQuery || activeFilters.aps_level || activeFilters.capability 
                    ? 'No examples match your filters' 
                    : 'No work examples yet. Add your first example!'}
                </p>
              ) : (
                filteredExamples.map((example, index) => (
                  <div
                    key={example.id}
                    data-testid={`example-card-${index}`}
                    className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 transition-all duration-200"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-sm text-foreground">{example.title}</h3>
                      <Badge className="bg-accent/10 text-accent hover:bg-accent/20">{example.aps_level}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{example.example_text}</p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {example.capabilities.slice(0, 2).map(cap => (
                        <Badge key={cap} variant="outline" className="text-xs">{cap.substring(0, 20)}...</Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        data-testid={`use-example-${index}`}
                        size="sm"
                        variant="outline"
                        onClick={() => handleUseExample(example)}
                        className="flex-1 text-xs"
                      >
                        <FileText className="h-3 w-3 mr-1" />
                        Use for Assessment
                      </Button>
                      <Button
                        data-testid={`edit-example-${index}`}
                        size="sm"
                        variant="ghost"
                        onClick={() => handleEditExample(example)}
                      >
                        <Edit2 className="h-3 w-3" />
                      </Button>
                      <Button
                        data-testid={`delete-example-${index}`}
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeleteExample(example.id)}
                        className="hover:text-red-600"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Main Area - Assessment Chat */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <div className="p-4 md:p-6 border-b border-border bg-white">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-accent" />
              <h2 className="text-xl font-semibold text-primary">AI Assessment</h2>
            </div>
            <p className="text-sm text-muted-foreground mt-1">Paste or select a work example for ILS framework assessment</p>
          </div>

          <ScrollArea className="flex-1 p-4 md:p-6">
            <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
              {/* Assessment Input */}
              <div className="bg-surface border border-border rounded-lg p-4 md:p-6">
                <Textarea
                  data-testid="assessment-textarea"
                  placeholder="Paste your work example here for assessment...\n\nExample: Led a cross-functional team project that improved service delivery by 25% through strategic stakeholder engagement and innovative process improvements..."
                  value={assessmentText}
                  onChange={(e) => setAssessmentText(e.target.value)}
                  className="min-h-[150px] md:min-h-[200px] mb-4 text-sm md:text-base"
                />
                <div className="flex gap-2">
                  <Button
                    data-testid="assess-button"
                    onClick={handleAssess}
                    disabled={isAssessing || !assessmentText.trim()}
                    className="bg-accent hover:bg-accent/90 text-white"
                  >
                    {isAssessing ? (
                      <><div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" /> Assessing...</>
                    ) : (
                      <><Sparkles className="h-4 w-4 mr-2" /> Assess Against APS ILS</>
                    )}
                  </Button>
                  {assessmentText && (
                    <Button
                      variant="outline"
                      onClick={() => { setAssessmentText(''); setAssessmentResult(null); }}
                    >
                      <X className="h-4 w-4 mr-2" /> Clear
                    </Button>
                  )}
                </div>
              </div>

              {/* Assessment Result */}
              {assessmentResult && (
                <div className="bg-card border border-border rounded-lg p-4 md:p-6" data-testid="assessment-result">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-2">
                      <BookOpen className="h-5 w-5 text-accent" />
                      <h3 className="text-lg font-semibold text-primary">Assessment Result</h3>
                    </div>
                    <Button
                      data-testid="save-assessment-button"
                      size="sm"
                      onClick={handleSaveAssessment}
                      className="bg-primary hover:bg-primary/90"
                    >
                      <Save className="h-4 w-4 mr-2" /> Save Assessment
                    </Button>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-foreground font-sans">{assessmentResult}</pre>
                  </div>
                </div>
              )}
              <div ref={assessmentEndRef} />
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* Add/Edit Example Dialog */}
      <Dialog open={showAddForm} onOpenChange={setShowAddForm}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedExample ? 'Edit Work Example' : 'Add Work Example'}</DialogTitle>
            <DialogDescription>Fill in the details of your work example</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmitExample} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Title</label>
              <Input
                data-testid="form-title"
                required
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="e.g., Cross-functional project leadership"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Example Text</label>
              <Textarea
                data-testid="form-example-text"
                required
                value={formData.example_text}
                onChange={(e) => setFormData(prev => ({ ...prev, example_text: e.target.value }))}
                className="min-h-[150px]"
                placeholder="Describe your work example using the STAR format (Situation, Task, Action, Result)..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Role</label>
                <Input
                  data-testid="form-role"
                  required
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  placeholder="e.g., Policy Officer"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">APS Level</label>
                <Select value={formData.aps_level} onValueChange={(val) => setFormData(prev => ({ ...prev, aps_level: val }))}>
                  <SelectTrigger data-testid="form-aps-level">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {APS_LEVELS.map(level => (
                      <SelectItem key={level} value={level}>{level}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Capabilities (comma-separated)</label>
              <Input
                data-testid="form-capabilities"
                value={formData.capabilities.join(', ')}
                onChange={(e) => handleArrayInput('capabilities', e.target.value)}
                placeholder="e.g., Achieves Results, Communicates with Influence"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Behaviours (comma-separated)</label>
              <Input
                data-testid="form-behaviours"
                value={formData.behaviours.join(', ')}
                onChange={(e) => handleArrayInput('behaviours', e.target.value)}
                placeholder="e.g., Takes responsibility, Shows initiative"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Tags (comma-separated)</label>
              <Input
                data-testid="form-tags"
                value={formData.tags.join(', ')}
                onChange={(e) => handleArrayInput('tags', e.target.value)}
                placeholder="e.g., leadership, stakeholder management, project delivery"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button data-testid="submit-form-button" type="submit" className="flex-1 bg-primary hover:bg-primary/90">
                {selectedExample ? 'Update Example' : 'Add Example'}
              </Button>
              <Button type="button" variant="outline" onClick={resetForm}>
                Cancel
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default App;