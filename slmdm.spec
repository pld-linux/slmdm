# NOTE: no SMP drivers for now - I don't know if these binaries would work?
# TODO: test it on SMP and add SMP modules or update above comment
Summary:	Smart Link soft modem drivers
Summary(pl):	Sterowniki do modemów programowych Smart Link
Name:		slmdm
Version:	2.6.16
%define	_rel	1
Release:	%{_rel}
License:	BSD almost without source
Group:		Base/Kernel
Vendor:		Smart Link Ltd. <http://www.smlink.com/>
Source0:	http://www.smlink.com/download/Linux/%{name}-%{version}.tar.gz
Patch0:		%{name}-2.4.20.patch
URL:		http://www.smlink.com/download/Linux/
%{!?_without_dist_kernel:BuildRequires:	kernel-headers}
BuildRequires:	%{kgcc_package}
ExclusiveArch:	%{ix86}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Smart Link soft modem drivers.

%description -l pl
Sterowniki do modemów programowych Smart Link.

%package -n kernel-char-slmdm
Summary:	Linux kernel drivers for Smart Link soft modem
Summary(pl):	Sterowniki j±dra Linuksa dla modemów programowych Smart Link
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{!?_without_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-char-slmdm
Linux kernel drivers for Smart Link soft modem.

%description -n kernel-char-slmdm -l pl
Sterowniki j±dra Linuksa dla modemów programowych Smart Link.

%prep
%setup -q
# patch needed since vanilla 2.4.20 or PLD's 2.4.19-2.x
%if %(grep -q urb_t %{_kernelsrcdir}/include/linux/usb.h ; echo $?)
%patch -p1
%endif

%build
KI="%{_kernelsrcdir}/include"
MV="-DMODVERSIONS --include ${KI}/linux/modversions.h"
CF="-Wall %{rpmcflags} -fomit-frame-pointer"
%{__make} \
	CC="%{kgcc}" \
	CFLAGS="${CF} -D__KERNEL__ -DMODULE -DEXPORT_SYMTAB -I. -I${KI} ${MV}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},/lib/modules/%{_kernel_ver}/misc}

install slver $RPM_BUILD_ROOT%{_bindir}
install slmdm.o slfax.o slamrmo.o slusb.o \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-char-slmdm
/sbin/depmod -a

%postun	-n kernel-char-slmdm
/sbin/depmod -a

%files
%defattr(644,root,root,755)
%doc COPYRIGHT Changes FAQ README
%attr(755,root,root) %{_bindir}/*

%files -n kernel-char-slmdm
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.o*
