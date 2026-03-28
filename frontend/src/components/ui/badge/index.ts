import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Badge } from './Badge.vue'

export const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-full border px-3 py-1 text-xs font-light tracking-tight w-fit whitespace-nowrap shrink-0 [&>svg]:size-3.5 gap-1.5 [&>svg]:pointer-events-none focus-visible:ring-2 focus-visible:ring-slate-900/20 overflow-hidden transition-all duration-500",
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-slate-900 text-white',
        secondary:
          'border-transparent bg-slate-100 text-slate-700',
        destructive:
          'border-transparent bg-red-600 text-white focus-visible:ring-red-600/20',
        outline:
          'border-slate-200 bg-white/80 text-slate-700 backdrop-blur-sm',
        success:
          'border-transparent bg-emerald-50 text-emerald-700 border-emerald-200',
        warning:
          'border-transparent bg-amber-50 text-amber-700 border-amber-200',
        muted:
          'border-transparent bg-slate-50 text-slate-500 border-slate-100',
        glass:
          'border-white/30 bg-white/60 backdrop-blur-md text-slate-700',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)
export type BadgeVariants = VariantProps<typeof badgeVariants>