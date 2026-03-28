import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2.5 whitespace-nowrap rounded-full text-sm font-light tracking-tight transition-all duration-500 disabled:pointer-events-none disabled:opacity-40 [&_svg]:pointer-events-none [&_svg:not([class*="size-"])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-slate-900/20 aria-invalid:ring-slate-400/20',
  {
    variants: {
      variant: {
        default:
          'bg-slate-900 text-white hover:bg-slate-800 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-900/10',
        destructive:
          'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600/20',
        outline:
          'border border-slate-200 bg-transparent text-slate-900 hover:bg-slate-50 hover:border-slate-300',
        secondary:
          'bg-slate-100 text-slate-900 hover:bg-slate-200',
        ghost:
          'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
        link:
          'text-slate-900 underline-offset-4 hover:underline',
        glass:
          'bg-white/80 backdrop-blur-md border border-white/30 text-slate-900 shadow-sm hover:bg-white/90 hover:shadow-md',
      },
      size: {
        default: 'h-11 px-5 py-2.5 has-[>svg]:px-4',
        sm: 'h-10 gap-2 px-4 has-[>svg]:px-3.5',
        lg: 'h-12 px-7 has-[>svg]:px-5 text-base',
        icon: 'size-11',
        'icon-sm': 'size-10',
        'icon-lg': 'size-12',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)
export type ButtonVariants = VariantProps<typeof buttonVariants>