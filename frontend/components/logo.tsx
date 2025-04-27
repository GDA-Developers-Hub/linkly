export function Logo({ size = 24 }: { size?: number }) {
  return (
    <div className="rounded-full bg-primary flex items-center justify-center" style={{ width: size, height: size }}>
      <span className="text-primary-foreground font-bold" style={{ fontSize: size * 0.5 }}>
        L
      </span>
    </div>
  )
}
