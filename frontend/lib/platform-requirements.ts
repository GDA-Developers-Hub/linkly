export interface PlatformRequirements {
    maxCharacters: number;
    maxHashtags: number;
    maxMedia: number;
    supportedMediaTypes: string[];
    bestPractices: {
      captionStyle: string;
      hashtagPlacement: 'inline' | 'end';
      emojiRecommended: boolean;
      mentionsLimit?: number;
    };
  }
  
  export const platformRequirements: Record<string, PlatformRequirements> = {
    instagram: {
      maxCharacters: 2200,
      maxHashtags: 30,
      maxMedia: 10,
      supportedMediaTypes: ['image', 'video', 'carousel'],
      bestPractices: {
        captionStyle: 'conversational with line breaks, emoji-friendly',
        hashtagPlacement: 'end',
        emojiRecommended: true,
      },
    },
    twitter: {
      maxCharacters: 280,
      maxHashtags: 3,
      maxMedia: 4,
      supportedMediaTypes: ['image', 'video', 'gif'],
      bestPractices: {
        captionStyle: 'concise and engaging',
        hashtagPlacement: 'inline',
        emojiRecommended: true,
        mentionsLimit: 10,
      },
    },
    facebook: {
      maxCharacters: 63206,
      maxHashtags: 10,
      maxMedia: 10,
      supportedMediaTypes: ['image', 'video', 'carousel', 'link'],
      bestPractices: {
        captionStyle: 'detailed with paragraphs',
        hashtagPlacement: 'end',
        emojiRecommended: true,
      },
    },
    linkedin: {
      maxCharacters: 3000,
      maxHashtags: 5,
      maxMedia: 9,
      supportedMediaTypes: ['image', 'video', 'document'],
      bestPractices: {
        captionStyle: 'professional and informative',
        hashtagPlacement: 'end',
        emojiRecommended: false,
      },
    },
  }
  
  export function getPlatformRequirements(platform: string): PlatformRequirements {
    return platformRequirements[platform.toLowerCase()] || platformRequirements['twitter'];
  }
  
  export function validateContentForPlatform(content: string, platform: string): { 
    valid: boolean; 
    errors: string[];
  } {
    const requirements = getPlatformRequirements(platform);
    const errors: string[] = [];
  
    if (content.length > requirements.maxCharacters) {
      errors.push(`Content exceeds ${platform}'s ${requirements.maxCharacters} character limit`);
    }
  
    const hashtagCount = (content.match(/#\w+/g) || []).length;
    if (hashtagCount > requirements.maxHashtags) {
      errors.push(`Too many hashtags for ${platform} (max: ${requirements.maxHashtags})`);
    }
  
    return {
      valid: errors.length === 0,
      errors,
    };
  }