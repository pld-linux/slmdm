# NOTE: no SMP drivers for now - I don't know if these binaries would work?
# TODO: test it on SMP and add SMP modules or update above comment
Summary:	Smart Link Soft Modem.
Name:		kernel-char-slmdm
Vendor:		Smart Link Ltd.
Version:	2.7.9
Release:	0.2
License:	Smart Link Ltd.
Group:		Applications/Communications
Source0:	slmdm-%{version}.tar.gz
URL:		http://linmodems.technion.ac.al/resources.html
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
SmartLink Software Modem.

%package amr
Summary:	Smart Link Soft Modem AMR/PCI component.
Group:		Applications/Communications
Requires:	kernel-char-slmdm
Conflicts:	kernel-char-slmdm-usb

%description amr
SmartLink Software Modem. HW drivers for HAMR5600 based
AMR/CNR/MDC/ACR modem cards and SmartPCI56, SmartPCI561 based PCI
modem cards.

%package usb
Summary:	Smart Link Soft Modem USB component.
Group:		Applications/Communications
Requires:	kernel-char-slmdm
Conflicts:	kernel-char-slmdm-amr

%description usb
SmartLink Software Modem. HW driver for SmartUSB56 based USB modem.

%define modules_conf /etc/modules.conf
# Used at home...
# %define _kernelsrcdir /usr/src/linux-2.4.20-wolk/include/
# %define _kernel_ver 2.4.20-wolk

%prep

%setup -q -n slmdm-%{version}

%build
%{__make} KERNEL_INCLUDES=%{_kernelsrcdir}

%install
rm -rf $RPM_BUILD_ROOT
# We cannot do it this way - it requires root privileges at this stage (adamg)
# %{__make} prefix_dir=$RPM_BUILD_ROOT install spec-file-lists
install -dD $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install -dD $RPM_BUILD_ROOT/%{_sysconfdir}
cp -f slmdm.o slusb.o slfax.o slamrmo.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
cp -f country.dat $RPM_BUILD_ROOT%{_sysconfdir}/country.dat

%post
if [ "$1" = 1 ] ; then
	cp %modules_conf %modules_conf.slmdm && \
	  grep -v 'slmodem' %modules_conf.slmdm > %modules_conf
	echo 'alias char-major-212 slmodem' >> %modules_conf
	echo 'alias slmodem off' >> %modules_conf
fi
depmod -a
mknod -m 666 /dev/ttySL0 -c 212 0
ln -sf /dev/ttySL0 /dev/modem

%post usb
cp %modules_conf %modules_conf.slusb && \
  sed -e 's/^alias slmodem .*$/alias slmodem slusb/' %modules_conf.slusb > %modules_conf
depmod -a

%post amr
cp %modules_conf %modules_conf.slamr && \
 sed -e 's/^alias slmodem .*$/alias slmodem slamrmo/' %modules_conf.slamr > %modules_conf
depmod -a

%postun usb
modprobe -r slusb
modprobe -r slfax
modprobe -r slmdm
if [ "$1" = 0 ]; then
	cp %modules_conf %modules_conf.slusb && \
	  sed -e 's/^alias slmodem slusb$/alias slmodem off/' %modules_conf.slusb > %modules_conf
fi
depmod -a

%postun amr
modprobe -r slamrmo
modprobe -r slfax
modprobe -r slmdm
if [ "$1" = 0 ]; then
	cp %modules_conf %modules_conf.slamr && \
	  sed -e 's/^alias slmodem slamrmo$/alias slmodem off/' %modules_conf.slamr > %modules_conf
fi
depmod -a

%preun
modprobe -r slamrmo
modprobe -r slusb
modprobe -r slfax
modprobe -r slmdm
if [ "$1" = 0 ]; then
	cp %modules_conf %modules_conf.slmdm && \
	grep -v 'slmodem' %modules_conf.slmdm > %modules_conf
	rm -f /var/lib/slmdm.data
fi
depmod -a

%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(644,root,root,755)
%attr(0644,root,root) /lib/modules/%{_kernel_ver}/misc/slmdm.o.gz
%attr(0644,root,root) /lib/modules/%{_kernel_ver}/misc/slfax.o.gz
#/dev/ttySL0
%config %{_sysconfdir}/country.dat
%doc README COPYRIGHT FAQ Changes

%files amr 
%defattr(644,root,root,755)
%attr(0644,root,root) /lib/modules/%{_kernel_ver}/misc/slamrmo.o.gz

%files usb 
%defattr(644,root,root,755)
%attr(0644,root,root) /lib/modules/%{_kernel_ver}/misc/slusb.o.gz
