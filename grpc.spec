# TODO:
# - system address_sorting and upb?
# - use shared grpc core in python modules
#
# Conditional build:
%bcond_without	apidocs		# (Python) API docs build
%bcond_without	python2		# CPython 2.x module
%bcond_without	python3		# CPython 3.x module
#
Summary:	RPC library and framework
Summary(pl.UTF-8):	Biblioteka i szkielet RPC
Name:		grpc
Version:	1.32.0
Release:	2
License:	Apache v2.0
Group:		Libraries
#Source0Download: https://github.com/grpc/grpc/releases
Source0:	https://github.com/grpc/grpc/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	e2afa783e763d5f6bc09b664b907ff25
Patch0:		%{name}-system-absl.patch
Patch1:		%{name}-sphinx.patch
Patch2:		%{name}-x32.patch
Patch3:		%{name}-libdir.patch
Patch4:		%{name}-system-re2.patch
Patch5:		%{name}-system-openssl.patch
URL:		https://grpc.io/
BuildRequires:	abseil-cpp-devel
BuildRequires:	c-ares-devel >= 1.13.0
BuildRequires:	cmake >= 3.5.1
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	openssl-devel
BuildRequires:	protobuf-devel >= 3.12
# with re2Config for cmake
BuildRequires:	re2-devel >= 20200801
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
BuildRequires:	zlib-devel
%if %{with python2}
BuildRequires:	python-Cython >= 0.23
BuildRequires:	python-modules >= 1:2.7
%endif
%if %{with python3}
BuildRequires:	python3-Cython >= 0.23
BuildRequires:	python3-modules >= 1:3.5
%endif
%if %{with apidocs}
BuildRequires:	python3-Sphinx >= 1.8.1
BuildRequires:	python3-six >= 1.10
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# require non-function grpc_core::ExecCtx::exec_ctx_ and grpc_core::ApplicationCallbackExecCtx::callback_exec_ctx_ symbols
%define		skip_post_check_so	libgrpc\\+\\+.so.* libgrpc\\+\\+_unsecure.so.*

%description
gRPC is a modern, open source, high-performance remote procedure call
(RPC) framework that can run anywhere. gRPC enables client and server
applications to communicate transparently, and simplifies the building
of connected systems.

%description -l pl.UTF-8
gRPC to nowoczesny, mający otwarty źródła, wydajny szkielet zdalnych
wywołań procedur (RPC - Remote Procedure Call). Pozwala na
przezroczystą komunikację klienta i serwera, upraszcza tworzenie
systemów połączonych.

%package devel
Summary:	Header files for gRPC library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki gRPC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for gRPC library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki gRPC.

%package apidocs
Summary:	API documentation for gRPC library
Summary(pl.UTF-8):	Dokumentacja API biblioteki gRPC
Group:		Documentation
%if "%{_rpmversion}" >= "4.6"
BuildArch:	noarch
%endif

%description apidocs
API documentation for gRPC library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki gRPC.

%package -n python-grpcio
Summary:	HTTP/2 based RPC framework
Summary(pl.UTF-8):	Szkielet RPC oparty na HTTP/2
Group:		Libraries/Python

%description -n python-grpcio
gRPC is a modern, open source, high-performance remote procedure call
(RPC) framework that can run anywhere. gRPC enables client and server
applications to communicate transparently, and simplifies the building
of connected systems.

%description -n python-grpcio -l pl.UTF-8
gRPC to nowoczesny, mający otwarty źródła, wydajny szkielet zdalnych
wywołań procedur (RPC - Remote Procedure Call). Pozwala na
przezroczystą komunikację klienta i serwera, upraszcza tworzenie
systemów połączonych.

%package -n python3-grpcio
Summary:	HTTP/2 based RPC framework
Summary(pl.UTF-8):	Szkielet RPC oparty na HTTP/2
Group:		Libraries/Python

%description -n python3-grpcio
gRPC is a modern, open source, high-performance remote procedure call
(RPC) framework that can run anywhere. gRPC enables client and server
applications to communicate transparently, and simplifies the building
of connected systems.

%description -n python3-grpcio -l pl.UTF-8
gRPC to nowoczesny, mający otwarty źródła, wydajny szkielet zdalnych
wywołań procedur (RPC - Remote Procedure Call). Pozwala na
przezroczystą komunikację klienta i serwera, upraszcza tworzenie
systemów połączonych.

%package -n python-grpcio-apidocs
Summary:	API documentation for Python gRPC library
Summary(pl.UTF-8):	Dokumentacja API biblioteki Pythona gRPC
Group:		Documentation
%if "%{_rpmversion}" >= "4.6"
BuildArch:	noarch
%endif

%description -n python-grpcio-apidocs
API documentation for Python gRPC library.

%description -n python-grpcio-apidocs -l pl.UTF-8
Dokumentacja API biblioteki Pythona gRPC.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
install -d build
cd build
%cmake .. \
	-DgRPC_INSTALL_CMAKEDIR:PATH=%{_lib}/cmake/grpc \
	-DgRPC_INSTALL_LIBDIR:PATH=%{_lib} \
	-DgRPC_ABSL_PROVIDER=package \
	-DgRPC_CARES_PROVIDER=package \
	-DgRPC_PROTOBUF_PROVIDER=package \
	-DgRPC_RE2_PROVIDER=package \
	-DgRPC_SSL_PROVIDER=package \
	-DgRPC_ZLIB_PROVIDER=package

%{__make}
cd ..

export GRPC_PYTHON_BUILD_SYSTEM_ABSL=1
export GRPC_PYTHON_BUILD_SYSTEM_CARES=1
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_RE2=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

%if %{with python2}
%py_build
%endif

%if %{with python3}
%if %{with apidocs}
export GRPC_PYTHON_ENABLE_DOCUMENTATION_BUILD=1
%endif
%py3_build
%endif

%if %{with apidocs}
sphinx-build-3 -b html doc/python/sphinx doc/python/sphinx/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

export GRPC_PYTHON_BUILD_SYSTEM_ABSL=1
export GRPC_PYTHON_BUILD_SYSTEM_CARES=1
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_RE2=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

%if %{with python2}
%py_install

%py_postclean
%endif

%if %{with python3}
%py3_install
%endif

install -d $RPM_BUILD_ROOT%{_docdir}
cp -pr doc $RPM_BUILD_ROOT%{_docdir}/%{name}-apidocs-%{version}
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-apidocs-%{version}/{csharp,python/sphinx,.gitignore}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CONCEPTS.md MAINTAINERS.md NOTICE.txt README.md TROUBLESHOOTING.md
%attr(755,root,root) %{_bindir}/grpc_cpp_plugin
%attr(755,root,root) %{_bindir}/grpc_csharp_plugin
%attr(755,root,root) %{_bindir}/grpc_node_plugin
%attr(755,root,root) %{_bindir}/grpc_objective_c_plugin
%attr(755,root,root) %{_bindir}/grpc_php_plugin
%attr(755,root,root) %{_bindir}/grpc_python_plugin
%attr(755,root,root) %{_bindir}/grpc_ruby_plugin
%attr(755,root,root) %{_libdir}/libgpr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgpr.so.12
%attr(755,root,root) %{_libdir}/libgrpc.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc.so.12
%attr(755,root,root) %{_libdir}/libgrpc_plugin_support.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc_plugin_support.so.1
%attr(755,root,root) %{_libdir}/libgrpc_unsecure.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc_unsecure.so.12
%attr(755,root,root) %{_libdir}/libgrpc++.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++.so.1
%attr(755,root,root) %{_libdir}/libgrpc++_alts.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_alts.so.1
%attr(755,root,root) %{_libdir}/libgrpc++_error_details.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_error_details.so.1
%attr(755,root,root) %{_libdir}/libgrpc++_reflection.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_reflection.so.1
%attr(755,root,root) %{_libdir}/libgrpc++_unsecure.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_unsecure.so.1
%attr(755,root,root) %{_libdir}/libgrpcpp_channelz.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpcpp_channelz.so.1
# TODO: use system libs instead
%attr(755,root,root) %{_libdir}/libaddress_sorting.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libaddress_sorting.so.12
%attr(755,root,root) %{_libdir}/libupb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libupb.so.12
%{_datadir}/grpc

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libgpr.so
%attr(755,root,root) %{_libdir}/libgrpc.so
%attr(755,root,root) %{_libdir}/libgrpc_plugin_support.so
%attr(755,root,root) %{_libdir}/libgrpc_unsecure.so
%attr(755,root,root) %{_libdir}/libgrpc++.so
%attr(755,root,root) %{_libdir}/libgrpc++_alts.so
%attr(755,root,root) %{_libdir}/libgrpc++_error_details.so
%attr(755,root,root) %{_libdir}/libgrpc++_reflection.so
%attr(755,root,root) %{_libdir}/libgrpc++_unsecure.so
%attr(755,root,root) %{_libdir}/libgrpcpp_channelz.so
%attr(755,root,root) %{_libdir}/libaddress_sorting.so
%attr(755,root,root) %{_libdir}/libupb.so
%{_includedir}/grpc
%{_includedir}/grpc++
%{_includedir}/grpcpp
%{_libdir}/cmake/grpc
%{_pkgconfigdir}/gpr.pc
%{_pkgconfigdir}/grpc.pc
%{_pkgconfigdir}/grpc_unsecure.pc
%{_pkgconfigdir}/grpc++.pc
%{_pkgconfigdir}/grpc++_unsecure.pc

%files apidocs
%defattr(644,root,root,755)
%{_docdir}/%{name}-apidocs-%{version}

%if %{with python2}
%files -n python-grpcio
%defattr(644,root,root,755)
%dir %{py_sitedir}/grpc
%{py_sitedir}/grpc/*.py[co]
%dir %{py_sitedir}/grpc/_cython
%attr(755,root,root) %{py_sitedir}/grpc/_cython/cygrpc.so
%{py_sitedir}/grpc/_cython/__init__.py[co]
%{py_sitedir}/grpc/_cython/_credentials
%{py_sitedir}/grpc/_cython/_cygrpc
%{py_sitedir}/grpc/aio
%{py_sitedir}/grpc/beta
%{py_sitedir}/grpc/experimental
%{py_sitedir}/grpc/framework
%{py_sitedir}/grpcio-%{version}-py*.egg-info
%endif

%if %{with python3}
%files -n python3-grpcio
%defattr(644,root,root,755)
%dir %{py3_sitedir}/grpc
%{py3_sitedir}/grpc/*.py
%{py3_sitedir}/grpc/__pycache__
%dir %{py3_sitedir}/grpc/_cython
%attr(755,root,root) %{py3_sitedir}/grpc/_cython/cygrpc.cpython-*.so
%{py3_sitedir}/grpc/_cython/__init__.py
%{py3_sitedir}/grpc/_cython/__pycache__
%{py3_sitedir}/grpc/_cython/_credentials
%{py3_sitedir}/grpc/_cython/_cygrpc
%{py3_sitedir}/grpc/aio
%{py3_sitedir}/grpc/beta
%{py3_sitedir}/grpc/experimental
%{py3_sitedir}/grpc/framework
%{py3_sitedir}/grpcio-%{version}-py*.egg-info
%endif

%if %{with apidocs}
%files -n python-grpcio-apidocs
%defattr(644,root,root,755)
%doc doc/python/sphinx/_build/html/{_static,*.html,*.js}
%endif
