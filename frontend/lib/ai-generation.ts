import { getPlatformRequirements } from './platform-requirements';

interface MediaInfo {
  type?: string;
  url?: string;
}

interface GenerationContext {
  existingContent?: string;
  platforms: string[];
  media?: MediaInfo[];
  scheduledTime?: Date;
  previousPosts?: any[];
}

export async function generateEnhancedContent(
  type: 'caption' | 'hashtags',
  context: GenerationContext
) {
  try {
    // Get requirements for all selected platforms
    const platformReqs = context.platforms.map(p => ({
      platform: p,
      requirements: getPlatformRequirements(p)
    }));

    // Find most restrictive requirements
    const minCharLimit = Math.min(...platformReqs.map(p => p.requirements.maxCharacters));
    const minHashtags = Math.min(...platformReqs.map(p => p.requirements.maxHashtags));

    // Analyze media if present
    const mediaAnalysis = context.media?.map(m => ({
      type: m.type || 'image',
      suggestedApproach: m.type?.includes('video') ? 'action-oriented' : 'descriptive'
    }));

    // Determine optimal content structure
    const contentStructure = determineContentStructure(platformReqs, mediaAnalysis);

    // Generate system prompt
    const systemPrompt = createSystemPrompt({
      type,
      platforms: platformReqs,
      mediaAnalysis,
      contentStructure,
      charLimit: minCharLimit,
      hashtagLimit: minHashtags,
      scheduledTime: context.scheduledTime,
      existingContent: context.existingContent
    });

    // Make API call
    const response = await fetch('/api/ai/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type,
        prompt: context.existingContent || '',
        context: {
          platforms: context.platforms,
          mediaTypes: mediaAnalysis?.map(m => m.type),
          scheduledTime: context.scheduledTime?.toISOString(),
          contentStructure,
          systemPrompt
        }
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate content');
    }

    const data = await response.json();
    return data.content;

  } catch (error) {
    console.error('Enhanced generation error:', error);
    throw error;
  }
}

function determineContentStructure(
  platformReqs: Array<{ platform: string; requirements: any }>,
  mediaAnalysis?: Array<{ type: string; suggestedApproach: string }>
) {
  // Default structure
  const structure = {
    useEmoji: true,
    hashtagPlacement: 'end' as 'inline' | 'end',
    tone: 'casual',
    format: 'single-paragraph'
  };

  // Adjust based on platforms
  if (platformReqs.some(p => p.platform === 'linkedin')) {
    structure.useEmoji = false;
    structure.tone = 'professional';
    structure.format = 'multi-paragraph';
  }

  // Adjust based on media
  if (mediaAnalysis?.some(m => m.type === 'video')) {
    structure.format = 'action-oriented';
  }

  return structure;
}

function createSystemPrompt(params: {
  type: string;
  platforms: Array<{ platform: string; requirements: any }>;
  mediaAnalysis?: Array<{ type: string; suggestedApproach: string }>;
  contentStructure: any;
  charLimit: number;
  hashtagLimit: number;
  scheduledTime?: Date;
  existingContent?: string;
}) {
  const timeContext = params.scheduledTime ? getTimeContext(params.scheduledTime) : null;
  
  const prompt = `You are an expert social media content creator.
${params.type === 'caption' ? createCaptionPrompt(params) : createHashtagPrompt(params)}

Content Requirements:
- Maximum length: ${params.charLimit} characters
- Hashtag limit: ${params.hashtagLimit}
- Tone: ${params.contentStructure.tone}
- Format: ${params.contentStructure.format}
${params.contentStructure.useEmoji ? '- Include relevant emojis' : '- Minimal emoji usage'}

${timeContext ? `Timing Context:
${timeContext}` : ''}

${params.mediaAnalysis ? `Media Context:
- Type: ${params.mediaAnalysis.map(m => m.type).join(', ')}
- Approach: ${params.mediaAnalysis.map(m => m.suggestedApproach).join(', ')}` : ''}

${params.existingContent ? `Existing Content Style:
Maintain the tone and style of: "${params.existingContent}"` : ''}

Ensure the content is:
1. Engaging and authentic
2. Platform-appropriate
3. Optimized for the given context
4. Natural and conversational
5. Aligned with best practices for each platform`;

  return prompt;
}

function createCaptionPrompt(params: any) {
  return `Generate a compelling caption that:
- Resonates with ${params.platforms.map(p => p.platform).join(', ')} audiences
- Follows each platform's best practices
- Drives engagement and interaction
- Creates a cohesive narrative with any media
- Encourages sharing and saving`;
}

function createHashtagPrompt(params: any) {
  return `Generate strategic hashtags that:
- Are highly relevant to the content
- Mix popular and niche tags
- Follow platform-specific best practices
- Maximize discovery potential
- Are naturally integrated into the content`;
}

function getTimeContext(scheduledTime: Date) {
  const hour = scheduledTime.getHours();
  const dayOfWeek = scheduledTime.getDay();
  
  let timeOfDay = 'morning';
  if (hour >= 12 && hour < 17) timeOfDay = 'afternoon';
  if (hour >= 17 || hour < 5) timeOfDay = 'evening';

  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  
  return `- Scheduled for: ${days[dayOfWeek]} ${timeOfDay}
- Optimize for ${timeOfDay} audience engagement
- Consider typical ${days[dayOfWeek]} user behavior
- Adapt tone for ${timeOfDay} consumption`;
} 