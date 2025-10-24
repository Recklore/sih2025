import { cn } from "@/lib/utils";
import { AnimatedAvatar } from "@/components/ui/avatar-animated";

interface MessageBubbleProps {
  message: string;
  isBot?: boolean;
  timestamp?: string;
  isTyping?: boolean;
}

export const MessageBubble = ({ message, isBot = false, timestamp, isTyping = false }: MessageBubbleProps) => {
  return (
    <div className={cn(
      "flex gap-3 mb-4 animate-fade-in",
      !isBot && "flex-row-reverse"
    )}>
      {isBot && (
        <AnimatedAvatar size="sm" isActive={isTyping} />
      )}
      
      <div className={cn(
        "max-w-[80%] px-4 py-3 rounded-2xl shadow-sm",
        "transition-all duration-300 hover:shadow-md",
        isBot 
          ? "bg-chat-surface text-chat-text rounded-bl-md" 
          : "bg-gradient-primary text-white rounded-br-md"
      )}>
        {isTyping ? (
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-chat-text-light rounded-full animate-bounce [animation-delay:-0.3s]" />
            <div className="w-2 h-2 bg-chat-text-light rounded-full animate-bounce [animation-delay:-0.15s]" />
            <div className="w-2 h-2 bg-chat-text-light rounded-full animate-bounce" />
          </div>
        ) : (
          <p className="text-sm leading-relaxed">{message}</p>
        )}
        
        {timestamp && (
          <p className={cn(
            "text-xs mt-1 opacity-70",
            isBot ? "text-chat-text-light" : "text-white/70"
          )}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
};