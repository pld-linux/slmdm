# NOTE: no SMP drivers for now - I don't know if these binaries would work?
# TODO: test it on SMP and add SMP modules or update above comment
# 
# Conditional build:
%bcond_without	dist_kernel	# without kernel from distribution
#
Summary:	Smart Link soft modem drivers
Summary(pl):	Sterowniki do modemów programowych Smart Link
Name:		slmdm
Version:	2.7.14
%define	rel	0.2
Release:	%{rel}
License:	BSD almost without source
Vendor:		Smart Link Ltd.
Group:		Base/Kernel
# ftp://ftp.smlink.com/Update/linux/unsupported/ doesn't work
# http://linmodems.technion.ac.il/packages/smartlink/
Source0:	http://www.smlink.com/main/down/%{name}-%{version}.tar.gz
# Source0-md5:	2fb4e60d46a55c8e6445600b4ce4e921
Patch0:		%{name}-2.4.20.patch
Patch1:		%{name}-turnon-devfs.patch
URL:		http://linmodems.technion.ac.il/resources.html
%{?with_dist_kernel:BuildRequires:	kernel-headers}
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
ExclusiveArch:	%{ix86}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		modules_conf	/etc/modules.conf

%description
Smart Link soft modem drivers.

%description -l pl
Sterowniki do modemów programowych Smart Link.

%package -n kernel-char-slmdm
Summary:	Linux kernel drivers for Smart Link soft modem
Summary(pl):	Sterowniki j±dra Linuksa dla modemów programowych Smart Link
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	dev >= 2.8.0-31

%description -n kernel-char-slmdm
Linux kernel drivers for Smart Link soft modem.

%description -n kernel-char-slmdm -l pl
Sterowniki j±dra Linuksa dla modemów programowych Smart Link.

%package -n kernel-char-slmdm-amr
Summary:	Linux kernel driver for Smart Link soft modem AMR/PCI component
Summary(pl):	Sterownik j±dra Linuksa dla elementu AMR/PCI modemów programowych Smart Link
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires(post,postun):	kernel-char-slmdm
Requires:	kernel-char-slmdm
Conflicts:	kernel-char-slmdm-usb

%description -n kernel-char-slmdm-amr
Linux kernel drivers for Smart Link soft modem. This package contains
driver for HAMR5600 based AMR/CNR/MDC/ACR modem cards and SmartPCI56,
SmartPCI561 based PCI modem cards.

%description -n kernel-char-slmdm-amr -l pl
Sterowniki j±dra Linuksa dla modemów programowych Smart Link. Ten
pakiet zawiera sterownik do opartych na HAMR5600 kart modemowych
AMR/CNR/MDC/ACR oraz kart PCI SmartPCI56 i SmartPCI561.

%package -n kernel-char-slmdm-usb
Summary:	Linux kernel driver for Smart Link soft modem USB component
Summary(pl):	Sterownik j±dra Linuksa dla elementu USB modemów programowych Smart Link
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires(post,postun):	kernel-char-slmdm
Requires:	kernel-char-slmdm
Conflicts:	kernel-char-slmdm-amr

%description -n kernel-char-slmdm-usb
Linux kernel drivers for Smart Link soft modem. This package contains
driver for SmartUSB56 based USB modem.

%description -n kernel-char-slmdm-usb -l pl
Sterowniki j±dra Linuksa dla modemów programowych Smart Link. Ten
pakiet zawiera sterownik dla modemów USB opartych na SmartUSB56.

%prep
%setup -q
# patch needed since vanilla 2.4.20 or PLD's 2.4.19-2.x
%if %(grep -q iso_packet_descriptor_t %{_kernelsrcdir}/include/linux/usb.h ; echo $?)
%patch -p1
%endif
%patch1 -p1

%build
echo "[%{_kernel_ver}]"
KI="%{_kernelsrcdir}/include"
MV="-DMODVERSIONS --include ${KI}/linux/modversions.h"
CF="-Wall %{rpmcflags} -fomit-frame-pointer"
%{__make} \
	CC="%{kgcc}" \
	KERNEL_INCLUDES=%{_kernelsrcdir}/include \
	CFLAGS="${CF} -D__KERNEL__ -DMODULE -DEXPORT_SYMTAB -I. -I${KI} ${MV}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},/lib/modules/%{_kernel_ver}/misc,%{_sysconfdir}}

install slver $RPM_BUILD_ROOT%{_bindir}
install slmdm.o slfax.o slamrmo.o slusb.o \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc

install country.dat $RPM_BUILD_ROOT%{_sysconfdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-char-slmdm
if ! grep -q '^alias.*slmodem' %{modules_conf} ; then
	umask 027
	echo 'alias char-major-212 slmodem' >> %modules_conf
	echo 'alias slmodem off' >> %modules_conf
fi
%depmod %{_kernel_ver}

%postun -n kernel-char-slmdm
if [ "$1" = "0" ]; then
	umask 027
	grep -v '^alias.*slmodem' %{modules_conf} %{modules_conf}.slmdm
	mv -f %{modules_conf}.slmdm %{modules_conf}
fi
%depmod %{_kernel_ver}

%post -n kernel-char-slmdm-amr
umask 027
sed -e 's/^alias slmodem .*$/alias slmodem slamrmo/' \
	%{modules_conf} > %{modules_conf}.slusb
mv -f %{modules_conf}.slusb %{modules_conf}
%depmod %{_kernel_ver}

%postun -n kernel-char-slmdm-amr
if [ "$1" = "0" ]; then
	umask 027
	sed -e 's/^alias slmodem slamrmo$/alias slmodem off/' \
		%{modules_conf} > %{modules_conf}.slusb
	mv -f %{modules_conf}.slusb %{modules_conf}
fi
%depmod %{_kernel_ver}

%post -n kernel-char-slmdm-usb
umask 027
sed -e 's/^alias slmodem .*$/alias slmodem slusb/' \
	%{modules_conf} > %{modules_conf}.slusb
mv -f %{modules_conf}.slusb %{modules_conf}
%depmod %{_kernel_ver}

%postun -n kernel-char-slmdm-usb
if [ "$1" = 0 ]; then
	umask 027
	sed -e 's/^alias slmodem slusb$/alias slmodem off/' \
		%{modules_conf} > %{modules_conf}.slusb
	mv -f %{modules_conf}.slusb %{modules_conf}
fi
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
%doc README COPYRIGHT FAQ Changes
%attr(755,root,root) %{_bindir}/*
%config %{_sysconfdir}/country.dat

%files -n kernel-char-slmdm
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/slmdm.o*
/lib/modules/%{_kernel_ver}/misc/slfax.o*

%files -n kernel-char-slmdm-amr
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/slamrmo.o*

%files -n kernel-char-slmdm-usb
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/slusb.o*
