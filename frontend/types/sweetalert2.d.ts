declare module 'sweetalert2' {
  interface SweetAlertOptions {
    title?: string;
    text?: string;
    html?: string;
    icon?: 'success' | 'error' | 'warning' | 'info' | 'question';
    toast?: boolean;
    position?: 'top' | 'top-start' | 'top-end' | 'center' | 'center-start' | 'center-end' | 'bottom' | 'bottom-start' | 'bottom-end';
    showConfirmButton?: boolean;
    timer?: number;
    timerProgressBar?: boolean;
    [key: string]: any;
  }

  interface SweetAlertResult {
    isConfirmed: boolean;
    isDenied: boolean;
    isDismissed: boolean;
    value?: any;
    [key: string]: any;
  }

  function fire(options: SweetAlertOptions): Promise<SweetAlertResult>;
  function fire(title: string, text?: string, icon?: 'success' | 'error' | 'warning' | 'info' | 'question'): Promise<SweetAlertResult>;

  const swal: {
    fire: typeof fire;
    // Add other methods if needed
  };

  export default swal;
} 