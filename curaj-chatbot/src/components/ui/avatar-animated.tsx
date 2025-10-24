import { cn } from "@/lib/utils";
import avatarImage from "@/assets/chatbot-avatar.png";

interface AnimatedAvatarProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  isActive?: boolean;
}

export const AnimatedAvatar = ({ className, size = "md", isActive = false }: AnimatedAvatarProps) => {
  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-12 w-12", 
    lg: "h-16 w-16"
  };

  return (
    <div className={cn(
      "relative rounded-full overflow-hidden bg-gradient-primary",
      "transition-all duration-300",
      isActive && "animate-pulse-glow",
      sizeClasses[size],
      className
    )}>
      <img 
        src={avatarImage} 
        alt="Educational Assistant Avatar"
        className={cn(
          "w-full h-full object-cover transition-transform duration-300",
          "hover:scale-110",
          isActive && "animate-bounce-gentle"
        )}
      />
      {isActive && (
        <div className="absolute inset-0 bg-gradient-primary opacity-20 animate-pulse" />
      )}
    </div>
  );
};