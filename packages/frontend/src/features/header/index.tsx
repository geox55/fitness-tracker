import { cn } from '@/shared/lib/css';
import { useSession } from '@/shared/model/session';
import { Button } from '@/shared/ui/kit/button';
import { ModeToggle } from '@/shared/ui/kit/mode-toggle';

export function AppHeader() {
  const { session, logout } = useSession();

  return (
    <header
      data-slot="header"
      className={cn(
        'sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60',
        'dark:bg-background/80 dark:border-border',
      )}
    >
      <div className="container mx-auto flex h-14 px-4 items-center gap-4">
        <div className="text-xl font-semibold">DSL Executor</div>

        <div className="flex items-center gap-4 ml-auto">
          <ModeToggle />
          {session && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">{session.email}</span>
              <Button
                variant="outline"
                size="sm"
                className="hover:bg-destructive/10"
                onClick={() => logout()}
              >
                Выйти
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
